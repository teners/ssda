function nonEmpty() {
    var warning = document.getElementById("warning");
    $(warning).fadeOut(500)
    var fn = document.forms["form"]["firstname"].value;
    var ln = document.forms["form"]["lastname"].value
    var c = document.forms["form"]["city"].value
    var f = document.forms["form"]["agefrom"].value
    var t = document.forms["form"]["ageto"].value
    if (fn == "" && ln == "" && c == "" && f == "" && t == "") {
        $(warning).fadeIn(500);
        return false;
    }
    return true;
}