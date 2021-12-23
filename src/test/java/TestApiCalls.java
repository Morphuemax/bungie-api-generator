import Helpers.HttpUtils;
import lib.api.Destiny2;
import lib.enums.BungieMembershipType;
import lib.enums.DestinyComponentType;
import lib.enums.DestinyGameVersions;

import java.io.IOException;

import static lib.api.Destiny2.GetProfile;
import static lib.api.Destiny2.SearchDestinyPlayer;

public class TestApiCalls {
    public static void main(String[] args) throws IOException {
        System.out.println("Hello World");
        String fqn = TestApiCalls.class.getName();
        System.out.println("Name: "+ fqn);
        System.out.println("Class: "+TestApiCalls.class);
        HttpUtils util = new HttpUtils("99f1687a8ee64e66a8e8334a73513f19");
        var membership_id = 20639569L;
        var destinyMembershipId = 4611686018485616648L;
        var characterId = 2305843009410461773L;
        var enumSet = DestinyGameVersions.fromType(511);
        var response = GetProfile(destinyMembershipId, BungieMembershipType.TigerSteam, DestinyComponentType.Profiles, util);
        var versionsOwned = response.getResponse().getProfile().getData().getVersionsOwned();
        var versionSet = DestinyGameVersions.fromType(versionsOwned);
        for(var ver : versionSet){
            var a = ver.toString();
            System.out.print(a+", ");
        }
        System.out.println("\b\b");
        System.out.println("Response: " + response);
    }
}
