package safetynet;
import java.io.*;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;

import javax.servlet.annotation.WebFilter;
import javax.servlet.annotation.WebInitParam;

import com.braintreegateway.*;

import com.braintreegateway.exceptions.BraintreeException;
import com.braintreegateway.exceptions.NotFoundException;
import com.google.api.core.ApiFuture;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.firestore.DocumentReference;
import com.google.cloud.firestore.DocumentSnapshot;
import com.google.cloud.firestore.Firestore;
import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.cloud.FirestoreClient;
import spark.servlet.SparkApplication;

import static spark.Spark.*;


public class SafetyNetServlet implements SparkApplication {
    static private Firestore db;
    private DocumentReference transactions;
    private static BraintreeGateway gateway;

   public static void main(String[] args) {
       //Need keys to instantiate braintree gateway. Check enviroment vars then for config.properties file.
       String btEnviroment = "";
       String btMerchantId = "";
       String btPubKey = "";
       String btPrivKey = "";
       if(System.getenv("BT_ENVIRONMENT") != null && System.getenv("BT_MERCHANT_ID") != null && System.getenv("BT_PUBLIC_KEY") != null && System.getenv("BT_PRIVATE_KEY") != null) {
           btEnviroment = System.getenv("BT_ENVIRONMENT");
           btMerchantId = System.getenv("BT_MERCHANT_ID");
           btPubKey = System.getenv("BT_PUBLIC_KEY");
           btPrivKey = System.getenv("BT_PRIVATE_KEY");
       }
       else {
           InputStream inputStream = null;
           Properties properties = new Properties();

           //Get keys from file so can be excluded from Git
           try {
               inputStream = new FileInputStream("config.properties");
               properties.load(inputStream);
               btEnviroment = properties.getProperty("BT_ENVIRONMENT");
               btMerchantId = properties.getProperty("BT_MERCHANT_ID");
               btPubKey = properties.getProperty("BT_PUBLIC_KEY");
               btPrivKey = properties.getProperty("BT_PRIVATE_KEY");
           } catch (Exception e) {
               System.err.println("Exception: " + e);
           } finally {
               try {
                   inputStream.close();
               } catch (IOException | java.lang.NullPointerException e) {
                   System.err.println("Exception: " + e);
               }
           }
       }
       try {
           gateway = new BraintreeGateway(btEnviroment, btMerchantId, btPubKey, btPrivKey);
       }
       catch(BraintreeException | NullPointerException e) {
           System.err.print("Could not initialize Braintree Gateway" + e.toString());
           stop();
       }

       //Try to get google account credentials from json file, then env variable
       GoogleCredentials credentials = null;
       File googleJsonFile = new File("safetynet-f2326-07c9a87323d7.json");
       InputStream in = null;
       if(googleJsonFile.isFile()) {
           try {
               in = new FileInputStream(googleJsonFile);
           }
           catch(FileNotFoundException e) {
               System.err.println("Google Json not found" + e.getMessage());
               stop();
           }
           try {
               credentials = GoogleCredentials.fromStream(in);
           }
           catch (IOException e) {
               System.err.println("Could not create google credentials" + e.getMessage());
           }
       }
       else {
           String googleJson = System.getenv("GOOGLEJSON");
           InputStream serviceAccount = new ByteArrayInputStream(googleJson.getBytes(StandardCharsets.UTF_8));
           try {
               credentials = GoogleCredentials.fromStream(serviceAccount);
           }
           catch (IOException e) {
               System.err.println("Could not create google credentials" + e.getMessage());
           }
       }
       FirebaseOptions options = new FirebaseOptions.Builder().setCredentials(credentials).build();
       FirebaseApp.initializeApp(options);
       db = FirestoreClient.getFirestore();
       //Spark.init();
	   new SafetyNetServlet().init();
    
  }

    @Override
    public void init()
    {
        //Set port, if there exists an env var use that, otherwise default to 4567
        String port = System.getenv("PORT");
        if(port != null && !port.isEmpty())
            port(new Integer(port));
        else
            port(4567);



        get("/client_token/:userId", (req, res) -> {
        	String customerId = req.queryParams(":userId");
        	return generateClientToken(customerId);
        });
        get("/client_token", (req, res) -> {
            String customerId = req.queryParams("userId");
            String clientToken = generateClientToken(customerId);
            if(clientToken != null && !clientToken.isEmpty())
                return clientToken;
            return "500 clientToken null";
        });
        get("/hello", (req, res) -> {
        	return "Hello" + " " + req.queryParams("name");
        });
        
        post("/checkout", (req,res) -> {
        	String nonce = req.queryParams("payment_method_nonce");
        	String userId = req.queryParams("userId");
        	String groupId = req.queryParams("groupId");
        	String name = req.queryParams("name");
        	String email = req.queryParams("email");
        	BigDecimal amount = new BigDecimal(req.queryParams("amount"));
        	boolean customerExists = true;
        	try{
        	    Customer customer = gateway.customer().find(userId);
            }
            catch(NotFoundException e) {
                System.out.println("Existing Customer not found, will create new one");
                customerExists = false;
            }
            TransactionRequest request;
            if(customerExists) {
                request = new TransactionRequest()
                        .amount(amount)
                        .paymentMethodNonce(nonce)
                        .customField("groupid", groupId)
                        .customerId(userId)
                        .options()
                        .storeInVaultOnSuccess(true)
                        .submitForSettlement(true)
                        .done();
            }
            else {
                request = new TransactionRequest()
                        .amount(amount)
                        .paymentMethodNonce(nonce)
                        .customField("groupid", groupId)
                        .customer()
                         .id(userId)
                         .firstName(name)
                         .email(email)
                         .done()
                        .options()
                         .storeInVaultOnSuccess(true)
                         .submitForSettlement(true)
                         .done();
            }
        	Result<Transaction> result = gateway.transaction().sale(request);
        	if(result.isSuccess()) {
                String transId = result.getTarget().getId();
                System.out.println("Transaction GroupID = " +  groupId + " " + "UserID=" +userId);
                db.collection("transactions").document(transId).set(transactionToMap(result.getTarget()));
                updateGroup(groupId, result.getTarget());
                return transId;
            }
            else {
                for (ValidationError error : result.getErrors().getAllDeepValidationErrors()) {
                    System.out.println(error.getCode());
                    System.out.println(error.getMessage());
                }
            }
        	return "error" + result.getErrors().toString();
        });
        
        get("/hello/:name", (req, res) -> {
        	return "Hello" + " " + req.params(":name");
        });
    }

    private String generateClientToken(String userId) {
        String clientToken;
        ClientTokenRequest clientTokenRequest = new ClientTokenRequest().customerId(userId);
        clientToken = gateway.clientToken().generate(clientTokenRequest);
        System.out.println(clientToken);
        return clientToken;
    }
    private Map<String, Object> transactionToMap(Transaction trans) {
       Map<String, Object> data = new HashMap<>();
       data.put("userid", trans.getCustomer().getId());
       data.put("amount",trans.getAmount().toString());
       data.put("timestamp", trans.getCreatedAt().toString());
       data.put("groupId", trans.getCustomFields().get("groupid"));
       data.put("name",trans.getCustomer().getFirstName());
       return data;
    }
    private void updateGroup(String groupId, Transaction trans) throws Exception {
       if(groupId == null || groupId.isEmpty())
           return;
       ApiFuture<DocumentSnapshot> future = db.collection("Groups").document(groupId).get();
       DocumentSnapshot groupDoc = future.get();
       String amount = (String)groupDoc.get("funds");
       if(amount == null)
           return;
       BigDecimal amountBig = new BigDecimal(amount);
       BigDecimal result = amountBig.add(trans.getAmount());
       db.collection("Groups").document(groupId).update("funds",result.toPlainString());
    }
   @WebFilter(
            filterName = "SparkInitFilter", urlPatterns = {"/*"}, 
            initParams = {
                @WebInitParam(name = "applicationClass", value = "SafetyNetServlet")
        })
    public static class SparkInitFilter extends spark.servlet.SparkFilter {
    }
}
