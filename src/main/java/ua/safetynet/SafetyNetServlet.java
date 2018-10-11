package ua.safetynet;
import static spark.Spark.get;

import java.io.IOException;
import java.io.InputStream;
import java.io.FileInputStream;
import java.util.Properties;

import javax.servlet.annotation.WebFilter;
import javax.servlet.annotation.WebInitParam;

import com.braintreegateway.BraintreeGateway;
import com.braintreegateway.ClientTokenRequest;

import spark.servlet.SparkApplication;



public class SafetyNetServlet implements SparkApplication {
	BraintreeGateway gateway;
	
   public static void main(String[] args) {
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
        
        get("/hello", (req, res) -> {
        return "Hello" + " " + req.queryParams("name");
        });
        
        get("/client_token", (req, res) -> {
        	String customerId = req.queryParams("userId");
        	String clientToken = null;
        	ClientTokenRequest clientTokenRequest = new ClientTokenRequest().customerId(customerId);
        	clientToken = gateway.clientToken().generate(clientTokenRequest);
        	return clientToken;
        });
        
    }
    @WebFilter(
            filterName = "SparkInitFilter", urlPatterns = {"/*"}, 
            initParams = {
                @WebInitParam(name = "applicationClass", value = "SafetyNetServlet")
        })
    public static class SparkInitFilter extends spark.servlet.SparkFilter {
    }
}
