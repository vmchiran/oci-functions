# FN App Configuration
* idcs_introspection_endpoint	https://<idcs_host>.identity.oraclecloud.com/oauth2/v1/introspect
* idcs_token_endpoint			https://<idcs_host>.identity.oraclecloud.com/oauth2/v1/token
* apigw_idcs_app_client_id
* apigw_idcs_app_client_secret_ocid
* oic_idcs_app_client_id
* oic_idcs_app_client_secret_ocid
* oic_scope

# Deploy and invoke the function

    cd oci-apigw-oic-auth
    fn -v deploy --app <my-fn-app>

    echo -n '{"token":"Bearer <token-value>"}' | fn invoke <my-fn-app> oci-apigw-oic-auth

# Documentation
* [Protect OIC REST APIs with OCI API Gateway and OAuth2 – 2/2](https://mytechretreat.com/protect-oic-rest-apis-with-oci-api-gateway-and-oauth2-2-2/)
* [Authenticating Oracle Integration flows using OAuth token from 3rd party provider](https://blogs.oracle.com/integration/post/authenticating-oic-flows-through-third-party-bearer-token)