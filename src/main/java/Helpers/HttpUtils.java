package Helpers;// * To change this license header, choose License Headers in Project Properties.
// * To change this template file, choose Tools | Templates
// * and open the template in the editor.
// */
//package com.mycompany.bungieapi_library.Utilities.HttpUtilities;
//

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * @author pengu_000
 */

public class HttpUtils {

    private static final String HOST = "https://www.bungie.net/Platform";
    private static String apiKey;
    private OAuth oAuth;

    public HttpUtils(String apiKey) {
        new HttpUtils(apiKey, null);
    }

    public HttpUtils(String apiKey, OAuth oAuth) {
        this.apiKey = apiKey;
        this.oAuth = oAuth;
    }

    public JsonObject getBungieEndpoint(String endpoint) throws IOException {
        URL obj = new URL(endpoint);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        // Set header
        con.setRequestProperty("X-API-KEY", apiKey);

        int responseCode = con.getResponseCode();
        System.out.println("\nSending 'GET' request to Bungie.Net : " + con.getURL().toString());
        System.out.println("Response Code : " + responseCode);

        String response = getRequest(con);

        JsonParser parser = new JsonParser();
        JsonObject json = (JsonObject) parser.parse(response);

        return json;
    }

    public <T> JsonObject postBungieEndpoint(String endpoint, JsonObject requestBody) throws IOException {
        URL obj = new URL(endpoint);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();

        con.setRequestProperty("X-API-KEY", apiKey);
        con.setRequestProperty("Content-Type", "application/json");
        try {
            con.setRequestProperty("Authorization", "Bearer " + oAuth.getAccessToken());
        } catch (Exception e) {
            System.out.println("Helpers.OAuth Access Token not available.  Helpers.OAuth may not have been initialized.");
        }

        con.setDoOutput(true);

        HttpUtils.addRequestBody(con, requestBody.getAsString());

        String response = postRequest(con);
        JsonParser parser = new JsonParser();
        JsonObject json = (JsonObject) parser.parse(response);

        return json;
    }

    public static String getRequest(HttpURLConnection con) throws IOException {
        con.setRequestMethod("GET");
        return sendRequest(con);
    }

    public static String postRequest(HttpURLConnection con) throws IOException {
        con.setRequestMethod("POST");
        return sendRequest(con);
    }

    private static String sendRequest(HttpURLConnection con) {
        String response;
        try (BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()))) {
            String inputLine;
            response = "";
            while ((inputLine = in.readLine()) != null) {
                response += inputLine;
            }
        } catch (Exception e) {
            return null;
        }
        return response;
    }

    protected static void addRequestBody(HttpURLConnection con, String body) {
        try (OutputStream os = con.getOutputStream()) {
            byte[] input = body.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}