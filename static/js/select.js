var items = ko.observableArray();
var paidby;
var attendees;
var reader;
var compressed_data = null;
var viewModel = function (_text) {
    var self = this;
    var text = _text;

    self.multiSelectInitOptions = {
        nonSelectedText: text,
//        includeSelectAllOption: true,
    };
    self.items = items;//ko.observableArray([]);
    self.selectedItems = ko.observableArray([]);
    self.addItem = function() {
        self.items.push($("#email").val());
        $("#email").val("");
    };
    self.add = function(obj) {
        self.items.push(obj);
    }
    return self;
};
var submit = function(event){
    var msg = {};
    msg.summary = $("#summary").val();
    msg.transaction = {};
    if (compressed_data) {
        msg.data = compressed_data;
    }
    //        ko.toJSON(paidby.selectedItems()).remove()
    msg.transaction.paidby = paidby.selectedItems();
    msg.transaction.attendees = attendees.selectedItems();
    msg.transaction.amount = $("#amount").val();
    $("#submit").attr("disabled", "disabled");
    $("#submit").val("Submitting");
    $.post("/new_transaction", JSON.stringify(msg), function(ret){
        console.log(ret);
        setTimeout(function(){
            location.reload();
        }, 5000);
    }, "json");
    // console.log(msg);
    // console.log(JSON.stringify(msg));
};
var submitButton = function() {
    var self = this;
    self.submit = function() {
        var file = document.getElementById('filebox').files[0]; //Files[0] = 1st file
        if (!file) submit();
        reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            var img = new Image();
            img.onload = function() {
                var canvas = document.getElementById("canvas");
                canvas.width = 250;
                canvas.height = canvas.width * img.height / img.width;
                var ctx = canvas.getContext("2d");
                ctx.drawImage(img,0,0, canvas.width, canvas.height);
                compressed_data = canvas.toDataURL("image/png", 0.3);
                submit();
            };
            img.src = reader.result;
        }
    }
    return self;
}

$(document).ready(function() {
    paidby = new viewModel("paidby");
    ko.applyBindings(paidby, $('#paidby')[0]);
    attendees = new viewModel("attendees");
    ko.applyBindings(attendees, $('#attendees')[0]);
    var submit = new submitButton();
    ko.applyBindings(submit, $('#submit')[0]);
    for (var i = 0; i < candidates.length; ++i ) {
        paidby.add(candidates[i]);
    }
    $.ajaxSetup({
        contentType: "application/json; charset=utf-8"
    });
});
