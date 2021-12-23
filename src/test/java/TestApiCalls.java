import Helpers.HttpUtils;
import com.google.gson.JsonObject;
import lib.enums.BungieMembershipType;
import lib.enums.DestinyComponentType;
import lib.responses.DestinyProfileResponseResponse;
import lib.api.Destiny2;
import lib.responses.GeneralUserResponse;


import java.io.IOException;

import static lib.api.Destiny2.GetProfile;
import static lib.api.User.GetBungieNetUserById;

public class TestApiCalls {
    public static void main(String[] args) throws IOException {
        System.out.println("Hello World");
        String fqn = TestApiCalls.class.getName();
        System.out.println("Name: " + fqn);
        System.out.println("Class: " + TestApiCalls.class);
        String apiKey = "99f1687a8ee64e66a8e8334a73513f19";
        HttpUtils util = new HttpUtils(apiKey);
        Long dM_id = Long.parseLong("4611686018485616648");
        GeneralUserResponse response = GetBungieNetUserById(20639569L, util);
        DestinyProfileResponseResponse response2 = GetProfile(dM_id, BungieMembershipType.TigerSteam, DestinyComponentType.Profiles, util);
        DestinyProfileResponseResponse response3 = new DestinyProfileResponseResponse(util.getBungieEndpoint("/Destiny2/3/Profile/4611686018485616648/?components=100"));
    }
}
