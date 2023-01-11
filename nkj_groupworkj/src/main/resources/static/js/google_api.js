var redirect = " https://a7b8-1-160-23-171.jp.ngrok.io/";
var apikey = "AIzaSyC0jPQ_aKzKy8c-tgb51KsWlI9yenvrnYc";
var clientid = "1060838685118-9id0hmf1nuos4iuql3brnk33br99erva.apps.googleusercontent.com";
var broadcast_id;
var streamId;
var streamtoken;
var streamstatus;
var t=0;
var broadcaststatus;
var sign;
var name;
var password;
var email;
//初始化google api
gapi.load("client:auth2", function() {
    gapi.auth2.init({client_id: clientid,plugin_name: "hallo"});
  });

//載入api用戶函數
function loadClient() {
    gapi.client.setApiKey(apikey);
    return gapi.client.load("https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest")
        .then(function() { console.log("GAPI client loaded for API"); },
              function(err) { console.error("Error loading GAPI client for API", err); });
  }

//延遲功能函數(秒)
function delay(n){
    return new Promise(function(resolve){
        setTimeout(resolve,n*1000);
    });
}

//製作google auth2物件函數並且登入
function authenticate() {
    const googleauth = gapi.auth2.getAuthInstance();
    googleauth.isSignedIn.listen(updatesigninstatus);
  return googleauth
      .signIn({scope: "https://www.googleapis.com/auth/youtube.force-ssl",prompt:"consent",redirect_uri:redirect})
      .then(function(response) {
          console.log("Sign-in successful",response);
                		name=response.getBasicProfile().getName()
                        email=response.getBasicProfile().getEmail()
                        password=response.getBasicProfile().getId()
                        sign=true
          },
            function(err) { console.error("Error signing in", err); });
}

//更新登入狀態函數
function updatesigninstatus(issignedin){
    sign = issignedin
    console.log("Sign-in status: ", issignedin);
}

//登出函數
function signout(){
    const googleauth = gapi.auth2.getAuthInstance();
    name=null;
    email=null;
    password=null;
    sign=false;
    return googleauth.signOut();
}

//更新直播間狀態函數
function updatebroadcaststatus(){
    gapi.client.youtube.liveBroadcasts.list({
        "part":["id","status"],
        "maxResults": 1,
        "mine":true
    }).then(function(response){
        broadcaststatus = response.result["items"][0]["status"]["lifeCycleStatus"]
        console.log("response from updatebroadcaststatus",response)
    },
            function(err){
        console.error("err from updatebroadcaststatus",err)
        }
    )
}

//直播間狀態轉TESTING函數
function testinglive(){
    gapi.client.youtube.liveBroadcasts.transition({
        "broadcastStatus":"testing",
        "id": broadcast_id,
        "part":[
            "id","snippet"
        ]
    }).then(
            function(response){console.log("testinglive transition response",response)},
            function(err){console.error("error from test transition",err)})
}

//更新視訊流狀態函數
function updatestreamstatus(){
    gapi.client.youtube.liveStreams.list({
        "part":["id","status"],
        "maxResults": 1,
        "mine":true
    }).then(function(response){
        streamstatus = response.result["items"][0]["status"]["streamStatus"]
        console.log("response from updatestreamstatus",response)
    },
            function(err){console.error("Error liveStream status update ", err);})
}

//直播間啟動函數
function startlive(){
    t=0;
    gapi.client.youtube.liveBroadcasts.transition({
        "broadcastStatus": "live",
        "id": broadcast_id,
        "part": [
        "id","snippet"
        ]
    }).then(
            function(response){console.log("startlive transition response",response)},
            function(err){console.error("error from start transition",err)})
}

//一鍵執行直播函數
async function execute() {
    var time = document.getElementById("start_time");
    var title = document.getElementById("title");
    time = time.value+"+08:00"
    const live_stream = gapi.client.youtube.liveStreams.insert({
        "part": [
            "snippet","cdn","contentDetails","status"
          ],
          "resource": {
            "snippet": {
                "title": "video",
                "description": "A description of your video stream. This field is optional."
            },
            "cdn": {
              "frameRate": "60fps",
              "ingestionType": "rtmp",
              "resolution": "1080p"
            },
            "contentDetails": {
              "isReusable": true
            }
          }
        })
            .then(function(response) {
                    // Handle the results here (response.result has the parsed body).
                    var stream = response.result
                    streamId = stream["id"]
                    streamtoken = stream["cdn"]["ingestionInfo"]["streamName"]
                    streamstatus = stream["status"]["streamStatus"]
                    address = stream["cdn"]["ingestionInfo"]["ingestionAddress"]
                    document.getElementById("yourtoken").innerHTML="<br>1.開啟您的OBS軟體<br>2.按下來源左下方的+ 選擇瀏覽器，按下確定並將網址設置為 localhost:5000/video 後按下確定<br>3.設定-串流-伺服器輸入"+address+"<br>4.您的YOUTUBE直播金鑰輸入"+streamtoken+" 按下確認後即可開始串流<br>"+"(請確認您的youtube頻道-設定-頻道-進階設定-目標觀眾不設定在'我想針對每部影片個別設定'')"
                    },
                  function(err) { 
                        console.error("liveStreams_Execute error", err); 
                        }
                    );
    
    const broadcast = gapi.client.youtube.liveBroadcasts.insert({
        "part":[
            "id",
            "snippet",
            "contentDetails",
            "status"
        ],
        "resource":{
            "snippet":{
                "title":title.value,
                "scheduledStartTime":time,
                "actualStartTime":time
              },
            "status": {
                "privacyStatus": "public"
              }
        }
    }).then(function(response){
        broadcast_id = response.result.id
        console.log("broadcast_Response",response)
    },
    function(err){ console.error("liveBroadcasts_Execute error",err); }).then(function(res){
    gapi.client.youtube.liveBroadcasts.bind({
    "id":broadcast_id,
    "part":["snippet","status"],
    "streamId":streamId
    }).then(async function(response){
    console.log("bind_Response",response);
    while(streamstatus != "active" && t<=200){
        t +=20;
        updatestreamstatus();
        console.log(t);
        await delay(20);
     };
     testinglive();
     while(broadcaststatus != "testing" && t<=200){
        t +=20;
        updatebroadcaststatus();
       console.log(t);
         await delay(20);
     }
    startlive();
        },function(err){console.error("bind_Execute error", err);})
}) 
  return live_stream,broadcast;
}


