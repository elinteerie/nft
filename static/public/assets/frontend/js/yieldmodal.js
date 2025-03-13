$(document).ready(

   

    // $('#yieldbutton').click(
    
    $('#yieldmodal').on('show.bs.modal', function(e) {

 
    var $this = $(e.relatedTarget);
    var data_id = $this.data('id');
    var modal = $('#yieldmodal');


    let collectionz = document.getElementsByName('collectionName')
    // let ownerz = document.getElementsByName('CollectionOwner')
    let minimumz = document.getElementsByName('CollectionMinimum')
    let maximumz = document.getElementsByName('CollectionMaximum')
    let yieldz = document.getElementsByName('CollectionYield')
    let useyieldz = document.getElementsByName('Useyield')



    var $slideActive = $('.swiper-slide-active');

    var realIndex = $slideActive.data('swiper-slide-index')
    if(typeof realIndex !== 'undefined') {
        realIndex = $slideActive.index();
    }
  



    document.getElementById('collectionname').innerHTML = collectionz[realIndex].value;
    // document.getElementById('collectionowner').innerHTML = '@'.concat(ownerz[realIndex].value);
    document.getElementById('collectionminimum').innerHTML = minimumz[realIndex].value;
    document.getElementById('collectionmaximum').innerHTML = maximumz[realIndex].value;
    document.getElementById('collectionyield').innerHTML = yieldz[realIndex].value;
    document.getElementById('useyield').innerHTML = useyieldz[realIndex].value;




    // modal.find('#yieldform').attr('action', function (i,old) {
    //    return old + '/' + data_id;

       modal.find('#yieldform')

})     


);


    function calculate () {
    // $( document ).ready(function() {

    

        var $slideActive = $('.swiper-slide-active');

        var realIndex = $slideActive.data('swiper-slide-index')
        if(typeof realIndex !== 'undefined') {
            realIndex = $slideActive.index();
        }

        // $('#investamount').change(function () {
            var amountz = ($("#investamount").val() != "") ? parseFloat($("#investamount").val()) : 0;

            let minimumz = document.getElementsByName('CollectionMinimum')
            let maximumz = document.getElementsByName('CollectionMaximum')
            let useyieldz = document.getElementsByName('Useyield')
   
        //for investment form
            let collectionidz = document.getElementsByName('collectionID')
            let yieldz = document.getElementsByName('CollectionYield')




            yieldvalue = useyieldz[realIndex].value;
            mininimum = minimumz[realIndex].value;
            maximum = maximumz[realIndex].value;

        //for investment form
            
            collectionid = collectionidz[realIndex].value;
            collectionyield = yieldz[realIndex].value;



            // $("#investamount").attr({
            //     "max" : mininimum,        // substitute your own
            //     "min" : maximum          // values (or variables) here
            //  });            
  
            // const useyield =  10;  
            var useyield = (yieldvalue != "") ? parseFloat(yieldvalue) : 0;  
            var profit = amountz * useyield;
            // $('#total').val(profit);
            document.getElementById("profitreturn").innerHTML = (profit.toFixed(2)) + ' ETH'
            // document.getElementById("collectionowner").innerHTML = collectionyield



            //for investment form
            // document.getElementById("formprofit").innerHTML = profit.toFixed(2)

            document.getElementById("formprofit").value = profit.toFixed(2);
            document.getElementById("formcollectionid").value = collectionid;





            // document.getElementById('collectionminimum').innerHTML = maximum;
        // });
    
    }




// function calculate () {

//     // let yieldz = document.getElementsByName('CollectionYield')

//     var amountz = document.getElementsByName("investamount").value;
//     // var useyield =  yieldz[realIndex].value;
//     var useyield =  10;
//     profit = amountz * useyield
//     document.getElementById("profitreturn").innerHTML = profit;
//    } 

// function calculate () {
// // $( document ).ready(function() {
//     $('#investamount').change(function () {
//         var amountz = ($("#investamount").val() != "") ? parseFloat($("#investamount").val()) : 0;  
//         const useyield =  10;  
//         // var no = ($("#no").val() != "") ? parseFloat($("#no").val()) : 0;  
//         var profit = amountz * useyield;
//         // $('#total').val(profit);
//         document.getElementById("profitreturn").innerHTML = profit        
//     });

// }
// });





