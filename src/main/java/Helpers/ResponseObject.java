package Helpers;

import java.util.Map;
import com.google.gson.Gson;
import com.google.gson.JsonElement;

public class ResponseObject<T>{
    T Response;
    int ErrorCode;
    int ThrottleSeconds;
    String ErrorStatus;
    String Message;
    Map<String, String> MessageData;
    String DetailedErrorTrace;

    public ResponseObject(JsonElement jsonElement){
        Gson gson = new Gson();
        ResponseObject<T> temp = gson.fromJson(jsonElement, ResponseObject.class);
        this.Response = temp.getResponse();
        this.ErrorCode = temp.getErrorCode();
        this.ThrottleSeconds = temp.getThrottleSeconds();
        this.ErrorStatus = temp.getErrorStatus();
        this.Message = temp.getMessage();
        this.MessageData = temp.getMessageData();
        this.DetailedErrorTrace = temp.getDetailedErrorTrace();
    }

    public T getResponse(){
        return Response;
    }
    public int getErrorCode(){ return ErrorCode;}
    public int getThrottleSeconds() { return ThrottleSeconds; }
    public String getErrorStatus() { return ErrorStatus; }
    public String getMessage() { return Message; }
    public Map<String, String> getMessageData() { return MessageData; }
    public String getDetailedErrorTrace() { return DetailedErrorTrace; }
}