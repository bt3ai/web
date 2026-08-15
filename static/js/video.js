var myVideo1=document.getElementById("video1");
var btn_play1 = document.getElementById("play1");
var btn_pause1 = document.getElementById("pause1");
var myVideo2=document.getElementById("video2");
var btn_play2 = document.getElementById("play2");
var btn_pause2 = document.getElementById("pause2");

btn_play1.addEventListener("click", function() {
    play(myVideo1);
})
btn_pause1.addEventListener("click", function() {
    pause(myVideo1);
})
btn_play2.addEventListener("click", function() {
    play(myVideo2);
})
btn_pause2.addEventListener("click", function() {
    pause(myVideo2);
})

function play(myVideo){
      myVideo.play();
}
function pause(myVideo){
      myVideo.pause();
}
