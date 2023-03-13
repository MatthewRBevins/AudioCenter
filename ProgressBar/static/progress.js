async function alert(){
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
        }, 50 );


      }

    }

    counterInit( 0, 100 );
  });
  await hideBar()
  document.getElementById("clickme").style.display="none";
  document.getElementById("proceed").style.display="block";
  document.getElementById("bar").style.display = "none";
  document.getElementById("bar2").style.display = "none";
  }

function showBar() {
  document.getElementById("bar").style.display = "";
}
const hideBar = async () => {
  return new Promise((res)=>{
    setTimeout(()=>{
      res();}, 6500);});
}

function showText() {
  document.getElementById("text").style.display = "";
}