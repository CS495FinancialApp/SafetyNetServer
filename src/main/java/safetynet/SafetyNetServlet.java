package safetynet;
import static spark.Spark.get;
import static spark.Spark.post;
import static spark.Spark.head;
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

import spark.Spark;
import spark.servlet.SparkApplication;



public class SafetyNetServlet implements SparkApplication {
	BraintreeGateway gateway;
	
   public static void main(String[] args) {
	   //Spark.init();
	   new SafetyNetServlet().init();
    
  }

    @Override
    public void init()
    {
    	InputStream inputStream = null;
        Properties properties = new Properties();
        
        //Get keys from file so can be excluded from Git
        try {
            inputStream = new FileInputStream("config.properties");
            properties.load(inputStream);
        } catch (Exception e) {
            System.err.println("Exception: " + e);
        } finally {
            try { inputStream.close(); }
            catch (IOException e) { System.err.println("Exception: " + e); }
        }

        gateway = new BraintreeGateway(
            properties.getProperty("BT_ENVIRONMENT"),
            properties.getProperty("BT_MERCHANT_ID"),
            properties.getProperty("BT_PUBLIC_KEY"),
            properties.getProperty("BT_PRIVATE_KEY")
        		);
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
