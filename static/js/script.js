// to include html inside another html file
document.addEventListener("DOMContentLoaded", function(){
    let includes = document.getElementsByTagName('include');
    for(var i=0; i<includes.length; i++){
        let include = includes[i];
        load_file(includes[i].attributes.src.value, function(text){
            include.insertAdjacentHTML('afterend', text);
            include.remove();
        });
    }
    function load_file(filename, callback) {
        fetch(filename).then(response => response.text()).then(text => callback(text));
    }
});

//reservation date
var dateToday = new Date();
var dates = $("#arrival_date, #departure_date").datepicker({
    defaultDate: "+1w",
    changeMonth: true,
    numberOfMonths: 3,
    minDate: dateToday,
    onSelect: function(selectedDate) {
        var option = this.id == "arrival_date" ? "minDate" : "maxDate",
            instance = $(this).data("datepicker"),
            date = $.datepicker.parseDate(instance.settings.dateFormat || $.datepicker._defaults.dateFormat, selectedDate, instance.settings);
        dates.not(this).datepicker("option", option, date);
    }
});