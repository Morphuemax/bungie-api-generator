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
        HttpUtils.apiKey = apiKey;
        this.oAuth = oAuth;
    }

    public static String getRequest(HttpURLConnection con) throws IOException {
        con.setRequestMethod("GET");
        return readResponse(con);
    }

    public static String postRequest(HttpURLConnection con) throws IOException {
        con.setRequestMethod("POST");
        return readResponse(con);
    }

    static String readResponse(HttpURLConnection con) {
        String response;
        try (BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()))) {
            String inputLine;
            response = "";
            while ((inputLine = in.readLine()) != null) {
                response += inputLine;
            }
        } catch (NullPointerException | IOException e) {
            return "\"ErrorCode\":\"500\", \"DetailedErrorTrace\":\"Null Response\"}";
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

    public JsonObject getBungieEndpoint(String endpoint) throws IOException {

        URL obj = new URL(HOST + endpoint);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        try {
            con.setRequestMethod("GET");
            // Set header
            con.setRequestProperty("X-API-KEY", apiKey);
            con.setRequestProperty("Content-Type", "application/json");
            try {
                con.setRequestProperty("Authorization", "Bearer " + oAuth.getAccessToken());
            } catch (Exception e) {
                System.out.println("Helpers.OAuth Access Token not available.  Helpers.OAuth may not have been initialized.");
            }
        } catch (Exception e) {
            System.out.println("Failed Sending 'GET' request to Bungie.Net : " + con.getURL().toString());
            System.out.println("Response Code : " + con.getResponseCode());
            e.printStackTrace();
        }

        JsonParser parser = new JsonParser();
        if (con.getResponseCode() == 200) {
            String response = readResponse(con);
            JsonObject json = (JsonObject) parser.parse(response);
            return json;
        }

        return (JsonObject) parser.parse("{\"ErrorCode\":\"" + con.getResponseCode() + "\", \"DetailedErrorTrace\":\"" + con.getResponseMessage() + "\"}");
    }

    public JsonObject postBungieEndpoint(String endpoint, JsonObject requestBody) throws IOException {
        URL obj = new URL(HOST + endpoint);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("POST");

        con.setRequestProperty("X-API-KEY", apiKey);
        con.setRequestProperty("Content-Type", "application/json");
        try {
            con.setRequestProperty("Authorization", "Bearer " + oAuth.getAccessToken());
        } catch (Exception e) {
            System.out.println("\nHelpers.OAuth Access Token not available.  Helpers.OAuth may not have been initialized.");
        }

        con.setDoOutput(true);

        HttpUtils.addRequestBody(con, requestBody.getAsString());

        JsonParser parser = new JsonParser();
        if (con.getResponseCode() == 200) {
            String response = readResponse(con);
            JsonObject json = (JsonObject) parser.parse(response);
            return json;
        }
        return (JsonObject) parser.parse("{\"ErrorCode\":\"" + con.getResponseCode() + "\", \"DetailedErrorTrace\":\"" + con.getResponseMessage() + "\"}");
    }

    public JsonObject postBungieEndpoint(String endpoint) throws IOException {
        URL obj = new URL(HOST + endpoint);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();
        con.setRequestMethod("POST");

        con.setRequestProperty("X-API-KEY", apiKey);
        con.setRequestProperty("Content-Type", "application/json");
        try {
            con.setRequestProperty("Authorization", "Bearer " + oAuth.getAccessToken());
        } catch (Exception e) {
            System.out.println("\nHelpers.OAuth Access Token not available.  Helpers.OAuth may not have been initialized.");
        }

        JsonParser parser = new JsonParser();
        con.setDoOutput(true);
        if (con.getResponseCode() == 200) {
            String response = readResponse(con);
            JsonObject json = (JsonObject) parser.parse(response);
            return json;
        }

        return (JsonObject) parser.parse("{\"ErrorCode\":\"" + con.getResponseCode() + "\", \"DetailedErrorTrace\":\"" + con.getResponseMessage() + "\"}");
    }

    public boolean hasOAuth() {
        if (oAuth == null) return false;
        return oAuth.getAccessToken() != null;
    }

    protected OAuth getOAuth() {
        return oAuth;
    }

    public void addOAuth(OAuth oAuth) {
        this.oAuth = oAuth;
    }
}