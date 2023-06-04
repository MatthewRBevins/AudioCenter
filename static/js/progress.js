function counterInit( fValue, lValue, time ) {
  var progress = $('.progressbar .progress')
  var counter_value = parseInt( $('.counter').text() );
  console.log(counter_value)
  counter_value++;
  if( counter_value >= fValue && counter_value <= lValue ) {
    $('.counter').text( counter_value + '%' );
    progress.css({ 'width': counter_value + '%' });
    setTimeout( function() {
      counterInit( fValue, lValue, time );
    }, time );
  }
}

async function resetBar() {
  console.log("Resetting");
  if(parseInt( $('.counter').text() ) == 99) {
    $('.counter').text( 0 + '%' );
  }
}

async function alertModal(time){
  console.log("Alerting");
  if(parseInt( $('.counter').text() ) != 0 ) {
    $('.counter').text( 0 + '%' );
  }
  counterInit( 0, 99, time );
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