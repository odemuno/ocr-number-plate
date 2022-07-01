function click_both() {
    // image
    let photo_id = document.getElementById('textInput').value
    let theURL1='/photos/'+photo_id;
    console.log("Making a RESTful click_display request to the server!")
    fetch(theURL1)
        .then(response=>response.json()) // Convert response to JSON
        .then(function(response) {
            let img = document.getElementById('image') 
            img.src = response['img_src']
        });

    // plate number
    let theURL2='/plate/'+photo_id;
    console.log("Making a RESTful click_plate request to the server!")
    fetch(theURL2)
        .then(response=>response.json()) // Convert response to JSON
        .then(function(response) {
            document.getElementById('plate').innerHTML=response;
        });
    
}

function getRows(){
  let numrows = document.getElementById('numrows').value; 
  if(numrows.trim() === "" ) {
    document.getElementById("error").textContent = "You have not provided an ID";
  }

  else {
   
   let data = {rows : numrows};
      fetch("/datarows", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
      }).then(response=>response.json())
      .then(function(response) {
      console.log("Request complete! response:", response);
      if(response == ""){

      }
      else{
        
        var keys = [];
        var obj = JSON.parse(response)
        document.write("<table border==\"1\"><tr>");
        for (key in obj[0]) {
          console.log('prinkting')
          console.log(key)
          document.write('<td>' + key + '</td>');
        }
        document.write("</tr>");
        for (var i = 0; i < obj.length; i++) {
          document.write('<tr>');
          for (key in obj[i]) {
            document.write('<td>' + obj[i][key] + '</td>');
          }
          document.write('</tr>');
        }
        document.write("</table>");

      
      }

      });

    
  }
}