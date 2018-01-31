import React, { Component } from 'react';
import './App.css';
import Papa from 'papaparse';

// React
class App extends Component {
  render() {
    return (
      <div className="App">
      </div>
    );
  }
}

export default App;

// Keys are question types as displayed in the app's frontend.
// Values are question types as encoded in the app's backend.
var question_types = {
  "Single Choice": "single_sel",
  "Image": "image_sel",
  "Multiple Choice": "multi_sel",
  "Text Entry": "text",
};

// Test for Array find to check for an existing questionnaire.
// Returns Boolean.
function questionnaire_exists(questionnaire_array){
  return(this == questionnaire_array["title"]);
}

// Function to generate JSON for a question with responses iff responses are provided.
// Returns JSON object
function questions_responses(test, question_title, question_types, file_json_array_i, response_json){
  return(
    test ? {
      "title": question_title,
      "type": question_types[file_json_array_i["Response Type"]],
      "rows": response_json,
      "variable_name": file_json_array_i["Question Abbreviation"],
    } : {
      "title": question_title,
      "type": question_types[file_json_array_i["Response Type"]],
      "variable_name": file_json_array_i["Question Abbreviation"],
    }
  )
}

// Function to restructure results of Papaparse into specific JSON format.
// Returns Array of JSON objects.
function json_restructure(file_json_array) {
  var dbs_json = [];
  for (var i=0; i<file_json_array.length; i++){
    var questionnaire_title = file_json_array[i]["Questionnaire Name"] === file_json_array[i]["Questionnaire Abbreviation"] ? file_json_array[i]["Questionnaire Name"] : file_json_array[i]["Questionnaire Abbreviation"] + " (" + file_json_array[i]["Questionnaire Name"] + ")";
    var responses = [];
    if (file_json_array[i]["Response Type"] !== "Text Entry"){
      responses = file_json_array[i]["Response Options"].split("\n");
      if (responses.length < 2){
        responses = file_json_array[i]["Response Options"].split(",");
      };
      var response_json = [];
      for (var j=0; j<responses.length; j++){
        var response_value = responses[j].split("=");
        response_json.push(
          {
            "text": response_value[1].trim(),
            "value": response_value[0].trim(),
          }
        )
      }
    };
    var question_title = file_json_array[i]["Question"].trim();
    if (file_json_array[i]["Question Group Instruction"].trim().length > 0){
      question_title = file_json_array[i]["Question Group Instruction"].trim() + ": " + question_title;
    };
    var existing_questionnaire = dbs_json.find(questionnaire_exists, questionnaire_title);
    if (existing_questionnaire) {
      existing_questionnaire["questions"].push(questions_responses(responses.length, question_title, question_types, file_json_array[i], response_json));
    } else {
      dbs_json.push(
        {
          "activity_type": "survey",
          "mode": "basic",
          "frequency": "1",
          "title": questionnaire_title,
          "questions": [
            questions_responses(responses.length, question_title, question_types, file_json_array[i], response_json),
          ],
        }
      );
    };
    //if file_json_array[i]);
  };
  return(dbs_json);
}

// Function to create a list item link to download a created JSON object.
// Returns HTML <li>
function json_link(object){
  var li = document.createElement("li");
  var link = document.createElement("a");
  var text = document.createTextNode(object.title);
  link.setAttribute("href", "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(object, null, '  ')));
  link.setAttribute("download", encodeURIComponent(object.title.replace(/ /g,'_')) + ".json");
  link.appendChild(text);
  li.appendChild(link);
  return(li);
}

// Function to parse CSV
// Returns list of JSON objects
var papa_results = function(results, file){
  var object = json_restructure(results.data);
  console.log(object);
  console.log(object.length + " questionnaires extracted from " + file.name);
  var out_area = document.getElementById("json_out");
  var out_list = document.createElement("ul");
  out_list.setAttribute("style", "list-style:none;");
  out_area.appendChild(out_list);
  for (var i=0; i < object.length; i++){
    out_list.appendChild(json_link(object[i]));
  }
  var file_link = document.createElement("a");
  file_link.setAttribute("href", "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(object, null, '  ')));
  var object_name = file.name.replace(/.csv/g,'_csv') + ".json";
  var bold = document.createElement("b");
  file_link.setAttribute("download", encodeURIComponent(object_name));
  file_link.appendChild(document.createTextNode(object_name));
  bold.appendChild(file_link);
  var li = document.createElement("li");
  li.appendChild(bold);
  out_list.appendChild(li);
  return(object);
}

// prepare to look for file extensions
var re = /(?:\.([^.]+))?$/;
// get file(s)
var control = document.getElementById("your-files-selector");
control.addEventListener("change", function(event) {
  // When the control has changed, there are new files
  var i = 0,
      files = control.files,
      len = files.length;

  for (; i < len; i++){
    var file = files[i];
    var ext = re.exec(file.name)[1];
    console.log("Ext: " + ext);
    if(ext !== "csv"){
      alert("Please upload a CSV worksheet based on our template, not a " + ext + " file.");
    } else {
      Papa.parse(file, {
      	complete: papa_results,
        header: true,
        skipEmptyLines: true,
      });
    }
  }

}, false);
