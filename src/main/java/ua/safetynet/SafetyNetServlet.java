package ua.safetynet;
import static spark.Spark.get;

import javax.servlet.annotation.WebFilter;
import javax.servlet.annotation.WebInitParam;

import spark.servlet.SparkApplication;



public class SafetyNetServlet implements SparkApplication {

   public static void main(String[] args) {
    new SafetyNetServlet().init();
    }

    @Override
    public void init()
    {
        get("/hello", (req, res) -> {
        return "Hello" + " " + req.queryParams("name");
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
