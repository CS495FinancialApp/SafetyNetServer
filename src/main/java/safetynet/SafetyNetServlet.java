package safetynet;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigDecimal;
import java.io.FileInputStream;
import java.util.Properties;

import javax.servlet.annotation.WebFilter;
import javax.servlet.annotation.WebInitParam;

import com.braintreegateway.BraintreeGateway;
import com.braintreegateway.ClientTokenRequest;
import com.braintreegateway.Result;
import com.braintreegateway.Transaction;
import com.braintreegateway.TransactionRequest;

import com.braintreegateway.exceptions.BraintreeException;
import spark.Spark;
import spark.servlet.SparkApplication;

import static spark.Spark.*;


public class SafetyNetServlet implements SparkApplication {
	BraintreeGateway gateway;
	
   public static void main(String[] args) {
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
        //Need keys to instantiate braintree gateway. Check enviroment vars then for config.properties file.
        String btEnviroment = null;
        String btMerchantId = null;
        String btPubKey = null ;
        String btPrivKey = null;

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
                } catch (IOException e) {
                    System.err.println("Exception: " + e);
                }
            }
        }
        try {
            gateway = new BraintreeGateway(btEnviroment, btMerchantId, btPubKey, btPrivKey);
        }
        catch(BraintreeException e) {
            System.err.print("Could not initialize Braintree Gateway" + e.toString());
        }
        get("/client_token/:userId", (req, res) -> {
        	String customerId = req.queryParams(":userId");
        	return generateClientToken(customerId);
        });
        get("/client_token", (req, res) -> {
            String customerId = req.queryParams("userId");
            return generateClientToken(customerId);
        });
        get("/hello", (req, res) -> {
        	return "Hello" + " " + req.queryParams("name");
        });
        
        post("/checkout", (req,res) -> {
        	String nonce = req.queryParams("payment_method_nonce");
        	BigDecimal amount = new BigDecimal(req.queryParams("amount"));
        	TransactionRequest request = new TransactionRequest()
        			.amount(amount)
        			.paymentMethodNonce(nonce)
        			.options()
        			.submitForSettlement(true)
        			.done();
        	Result<Transaction> result = gateway.transaction().sale(request);
        	return result;
        });
        
        get("/hello/:name", (req, res) -> {
        	return "Hello" + " " + req.params(":name");
        });
    }

    private String generateClientToken(String userId) {
        String clientToken = null;
        ClientTokenRequest clientTokenRequest = new ClientTokenRequest().customerId(userId);
        clientToken = gateway.clientToken().generate(clientTokenRequest);
        System.out.println(clientToken);
        return clientToken;
    }
   @WebFilter(
            filterName = "SparkInitFilter", urlPatterns = {"/*"}, 
            initParams = {
                @WebInitParam(name = "applicationClass", value = "SafetyNetServlet")
        })
    public static class SparkInitFilter extends spark.servlet.SparkFilter {
    }
}
