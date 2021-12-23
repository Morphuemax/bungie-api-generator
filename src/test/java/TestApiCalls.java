import Helpers.HttpUtils;
import lib.enums.BungieMembershipType;
import lib.responses.DestinyProfileResponseResponse;
import lib.api.Destiny2;


import java.io.IOException;

public class TestApiCalls {
    public static void main(String[] args) throws IOException {
        System.out.println("Hello World");
        String fqn = TestApiCalls.class.getName();
        System.out.println("Name: " + fqn);
        System.out.println("Class: " + TestApiCalls.class);
        String apiKey = "99f1687a8ee64e66a8e8334a73513f19";
        HttpUtils util = new HttpUtils(apiKey);
        DestinyProfileResponseResponse response = getProfile(Long.getLong("4611686018485616648"), BungieMembershipType.TigerSteam, util);
    }
}
