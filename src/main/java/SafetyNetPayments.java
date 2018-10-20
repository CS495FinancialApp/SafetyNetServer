import java.io.InputStream;
import java.math.BigDecimal;
import java.io.FileInputStream;
import java.util.Properties;
import com.braintreegateway.BraintreeGateway;
import com.braintreegateway.ClientTokenRequest;
import com.braintreegateway.Result;
import com.braintreegateway.Transaction;
import com.braintreegateway.TransactionRequest;

import com.google.api.server.spi.auth.EspAuthenticator;
import com.google.api.server.spi.auth.common.User;
import com.google.api.server.spi.config.AnnotationBoolean;
import com.google.api.server.spi.config.Api;
import com.google.api.server.spi.config.ApiIssuer;
import com.google.api.server.spi.config.ApiIssuerAudience;
import com.google.api.server.spi.config.ApiMethod;
import com.google.api.server.spi.config.ApiNamespace;
import com.google.api.server.spi.config.Named;
import com.google.api.server.spi.config.Nullable;
import com.google.api.server.spi.response.UnauthorizedException;

@Api(
        name = "safetynet",
        version = "v1",
        namespace =
        @ApiNamespace(
                ownerDomain = "ua.safetynet",
                ownerName = "ua.safetynet",
                packagePath = ""
        ),
        // [START_EXCLUDE]
        issuers = {
                @ApiIssuer(
                        name = "firebase",
                        issuer = "https://securetoken.google.com/safetynet-f2326",
                        jwksUri =
                                "https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system"
                                        + ".gserviceaccount.com"
                )
        }
// [END_EXCLUDE]
)
// [END echo_api_annotation]
public class SafetyNetPayments{
    private BraintreeGateway gateway;

    public SafetyNetPayments() {
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
            catch (Exception e) { System.err.println("Exception: " + e); }
        }

        gateway = new BraintreeGateway(
                properties.getProperty("BT_ENVIRONMENT"),
                properties.getProperty("BT_MERCHANT_ID"),
                properties.getProperty("BT_PUBLIC_KEY"),
                properties.getProperty("BT_PRIVATE_KEY")
        );
    }


    @ApiMethod(name = "getToken")
    public ClientToken getClientToken(@Named("userId") String userId) {


        String token = null;
        ClientTokenRequest clientTokenRequest = new ClientTokenRequest().customerId(userId);
        token = gateway.clientToken().generate(clientTokenRequest);
        return new ClientToken(token);
    }

    @ApiMethod(name = "checkout")
    public Result<Transaction> checkout(@Named("nonce") String nonce,BigDecimal amount) {
        TransactionRequest request = new TransactionRequest()
                .amount(amount)
                .paymentMethodNonce(nonce)
                .options()
                .submitForSettlement(true)
                .done();
        return gateway.transaction().sale(request);
    }

    @ApiMethod(name = "hello")
    public ClientToken sayHello(@Named("name") String name) {
        return new ClientToken("Hello, " + name);
    }
}
