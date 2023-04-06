async function alertModal(time){
  $(document).ready(function() {

    var progress = $('.progressbar .progress')

    function counterInit( fValue, lValue ) {

      var counter_value = parseInt( $('.counter').text() );
      counter_value++;

      if( counter_value >= fValue && counter_value <= lValue ) {

        $('.counter').text( counter_value + '%' );
        progress.css({ 'width': counter_value + '%' });

        setTimeout( function() {
          counterInit( fValue, lValue );
        }, time );


      }

    }

    counterInit( 0, 100 );
  });
  await hideBar(100*time + 1500)
  }

function showBar() {
  document.getElementById("bar").style.display = "";
}
async function hideBar(time) {
  return new Promise((res)=>{
    setTimeout(()=>{
      res();}, time);});
}   

function showText() {
  document.getElementById("text").style.display = "";
}