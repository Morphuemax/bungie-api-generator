package Helpers;

import Helpers.HttpUtils;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Base64;

public class OAuth {
    private JsonObject oAuthJson;
    private String clientId;
    private String clientSecret;

    public OAuth(String clientId, String clientSecret) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
    }

    public void Authorize(HttpServletResponse response) throws IOException {
        //TODO: Generate random "state"
        response.sendRedirect("https://www.bungie.net/en/OAuth/Authorize?client_id=" + clientId + "&response_type=code");
    }

    public int Access(String authCode) throws IOException {
        String url = "https://www.bungie.net/Platform/app/oauth/token/";
        String urlParameters = "grant_type=authorization_code&code=" + authCode;
        String credentials = clientId + ":" + clientSecret;
        String encodedCredentials = Base64.getUrlEncoder().encodeToString(credentials.getBytes());

        URL obj = new URL(url);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();

        con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        con.setRequestProperty("Authorization", "Basic " + encodedCredentials);
        System.out.println("Sending 'POST' request to Bungie.Net : " + url);
        con.setDoOutput(true);

        HttpUtils.addRequestBody(con, urlParameters);

        String response = HttpUtils.postRequest(con);
        if (response != null) {
            JsonParser parser = new JsonParser();
            oAuthJson = (JsonObject) parser.parse(response);
            return oAuthJson.get("membership_id").getAsInt();
        } else {
            return -1;
        }
    }

    protected String getAccessToken() {
        return oAuthJson.get("access_token").getAsString();
    }

    protected String getRefreshToken() {
        return oAuthJson.get("refresh_token").getAsString();
    }

    public boolean Refresh() {
        return false;
    }
}