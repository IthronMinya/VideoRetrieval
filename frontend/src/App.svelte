<script>
// @ts-nocheck

  import { selected_images } from './stores.js';
  import ImageList from './ImageList.svelte';

  import Timer from './Timer.svelte';

  import VirtualList from '@sveltejs/svelte-virtual-list';
  
  import Button from '@smui/button';

  // @ts-ignore
  import Select, { Option } from '@smui/select';
  
  import Fab, { Icon } from '@smui/fab';

  import { onMount, onDestroy } from 'svelte';


  let timer;

  let lion_text_query = "";

  let start;
	let end;
  let image_items = [];
  let alpha = 0.1;

  let custom_result = "";

  let max_display_size = 2000;

  let test_image_av = false;

  let row_size;
  let prepared_display = null;

  $: {
    handleResize(image_items);
    prepared_display;
    filtered_lables;
  }

  let random_target = null;

  let clicked = 0;

  let datasets = ['V3C', 'Medical'];

  let models = ['clip-laion', 'clip-openai'];
 
  let value_dataset = 'V3C';

  let value_model = 'clip-laion';

  let username = "";

  let send_results = "";

  let action_log = [];

  let action_log_without_back_and_forth = [];
  let action_log_pointer = 0;

  let bayes_display = 10 * row_size;

  let dragged_url = null;

  let action_pointer = 0;

  let file = null;

  let allLabels = [];

  let allOccurrences = [];

  let allIds = [];

  let filtered_lables = [];

  let file_labels = [];

  initialization();

  function handleResize(){

    console.log(filtered_lables)
    row_size = Math.floor(window.innerWidth / 350);
    console.log(row_size);

    if (image_items[action_pointer] != null){
      console.log("resizing or reloading display");

      let rows = [];
      let row = -1;

      let s = 0
      for (let i = 0; i < image_items[action_pointer].length; i++) {
        
        if (image_items[action_pointer][i].hasOwnProperty('disabled') && !image_items[action_pointer][i]['disabled']) {
          if (s % row_size == 0){
            row = row + 1;
            rows[row] = [];
          }
          rows[row].push(image_items[action_pointer][i]);
          s += 1;
        }else if(image_items[action_pointer][i].hasOwnProperty('disabled') && image_items[action_pointer][i]['disabled']){
          // do nothing
        }else{
          if (s % row_size == 0){
            row = row + 1;
            rows[row] = [];
          }
          rows[row].push(image_items[action_pointer][i]);
          s += 1;
        }
      }


      start = 0;

      prepared_display = rows;

      console.log(prepared_display);

      create_chart();

    }else{
      prepared_display = null;
    }

  }

  onMount(() => {
    window.addEventListener('resize', handleResize);
    handleResize(); // Initialize the variable and check the threshold on component mount
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });

  onDestroy(() => {
    // Cleanup event listener on component destroy
    window.removeEventListener('resize', handleResize);
  });


  function noopHandler(evt) {
      evt.preventDefault();
  }
  
  function drop(evt) {

    evt.preventDefault();
    file = evt.dataTransfer.files[0];

    console.log(evt.dataTransfer.files);

    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();

      reader.onload = () => {
        dragged_url = reader.result;
      };

      reader.readAsDataURL(file);

      get_scores_by_image_upload();
    }
  }

  function send_results_custom(){
    timer.stop();

    send_results = custom_result;

    $selected_images = [];

    action_log.push({'method': 'send_custom_result', 'query': send_results, 'k': 0});
  }

  function send_results_single(event){
    timer.stop();

    send_results = event.detail.image_id;

    $selected_images = [];

    action_log.push({'method': 'send_single_result', 'query': send_results, 'k': 0});

  }

  function send_results_multiple(){
    timer.stop();

    send_results = " ";

    $selected_images.forEach((selection) => {
      send_results += `${selection}; `;
    });

    send_results = send_results.slice(0, -2); // remove last space and semicolon

    $selected_images = [];

    action_log.push({'method': 'send_multi_result', 'query': send_results, 'k': 0});
  }

  function download(content, fileName, contentType) {
      var a = document.createElement("a");
      var file = new Blob([content], {type: contentType});
      a.href = URL.createObjectURL(file);
      a.download = fileName;
      a.click();
  }

  function download_results(){

    const target = {'target': random_target[0]['id']};
    const full_data = [target].concat(action_log);

    console.log(full_data);

    var action_log_json = JSON.stringify(full_data);

    download(action_log_json, 'action_log.txt', 'text/plain');

  }

  async function get_test_image(){

    image_items = [];
    action_log = [];
    action_log_without_back_and_forth = [];

    initialization();

    action_pointer = 0;

    action_log_pointer = 1;

    $selected_images.forEach((selection) => {
      send_results += `${selection}; `;
    });
    
    $selected_images = [];

    timer.reset();
    timer.start();

    test_image_av = true;

    const imgElement = document.getElementById('testimage');

    try {
        const response = await fetch("http://acheron.ms.mff.cuni.cz:42032/getRandomFrame/");
        if (response.ok) {

          random_target = await response.json();
          
          let imageUrl = "http://acheron.ms.mff.cuni.cz:42032/images/" + String(random_target[0]["uri"]);

          console.log(imageUrl);

          try {
            const response_image = await fetch(imageUrl);
            if (response_image.ok) {

              // @ts-ignore
              imgElement.src = URL.createObjectURL(await response_image.blob());
            } else {
                console.error('Failed to fetch image.');
            }
          } catch (error) {
              console.error('Error:', error);
          }
        } else {
            console.error('Failed to get random image data.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
  
  }

  async function video_images(event) {
    
    const request_url = "http://acheron.ms.mff.cuni.cz:42032/getVideoFrames/";

    let selected_item = event.detail.image_id;

    action_log_without_back_and_forth.push({'method': 'show_video_frames', 'query': [selected_item[0], selected_item[1]], 'k': 50});

    action_log.push({'method': 'show_video_frames', 'query': [selected_item[0], selected_item[1]], 'k': 50});

    const request_body = JSON.stringify({
      item_id: String(selected_item[0]) + "_" + String(selected_item[1]),
      k: 50,
      add_features: 0
    });

    request_handler(request_url, request_body);
    
  }

  async function initialization() {

    // Read labels from the text file
    file_labels = await readTextFile('./assets/nounlist.txt');

    
    image_items[action_pointer] = null;

    action_log_without_back_and_forth.push({'method': 'initialization', 'query': '', 'k': 50});
    
    const request_url = "http://acheron.ms.mff.cuni.cz:42032/getVideoFrames/";

    try {
        const response = await fetch("http://acheron.ms.mff.cuni.cz:42032/getRandomFrame/");
        if (response.ok) {

          random_target = await response.json();

          console.log(random_target[0]["id"]);
          
          let random_id = random_target[0]["id"];

          const request_body = JSON.stringify({
            item_id: String(random_id[0]) + "_" + String(random_id[1]),
            k: 50,
            add_features: 0
          });

          request_handler(request_url, request_body, true);
          
        }
    } catch (error) {
        console.error('Error:', error);
    }
    
  }

  function handleKeypress(event){
    var key=event.keyCode || event.which;
    if (key==13){
      get_scores_by_text();
    }
  }

  async function request_handler(request_url, request_body, init=false, image_upload=false){

    prepared_display = null;

    action_log_pointer += 1;

    if(!init){
      while(image_items.length > action_pointer + 1){
        image_items.pop();
      }

      while(action_log_without_back_and_forth.length > action_log_pointer){
        action_log_without_back_and_forth.splice(action_log_without_back_and_forth.length - 2, 1);
      }

      image_items.push(null);

      action_pointer += 1;
           
    }


    let response;

    try {

      if(!image_upload){
        response = await fetch(request_url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: request_body
        });
      }else{
        response = await fetch(request_url, {
          method: 'POST',
          body: request_body
        });
      }


      if (!response.ok) {
        throw new Error('Request failed');
      }

      let responseData = await response.json();

      console.log(responseData);

      if (filtered_lables.length > 0){
        for (const [key, value] of Object.entries(responseData)) {
          responseData[key]['disabled'] = true;
        }

        for (const [key, value] of Object.entries(responseData)) {
          for(let i=0; i < filtered_lables.length; i++){
            if (responseData[key].label.includes(filtered_lables[i])) {
              responseData[key]['disabled'] = false;
            }
          }
        }
      }else{
        for (const [key, value] of Object.entries(responseData)) {
          responseData[key]['disabled'] = false;
        }
      }
      
      image_items[action_pointer] = responseData;
      handleResize();
      
      if(!init){
        $selected_images = [];
      }

    } catch (error) {
      console.error(error);
    }

  }

  async function get_scores_by_text() {

    action_log_without_back_and_forth.push({'method': 'textquery', 'query': lion_text_query, 'k': max_display_size});
    action_log.push({'method': 'textquery', 'query': lion_text_query, 'k': max_display_size});

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/textQuery/";

    const request_body = JSON.stringify({
      query: lion_text_query,
      k: max_display_size,
    });

    await request_handler(request_url, request_body);
  }

  async function get_scores_by_image(event) {

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQueryByID/";

    let selected_item = event.detail.image_id;

    action_log_without_back_and_forth.push({'method': 'image_internal_query', 'query': [selected_item[0], selected_item[1]], 'k': max_display_size});

    action_log.push({'method': 'image_internal_query', 'query': [selected_item[0], selected_item[1]], 'k': max_display_size});

    const request_body = JSON.stringify({
      video_id: selected_item[0],
      frame_id: selected_item[1],
      k: max_display_size,
    });

    console.log(request_body);


    await request_handler(request_url, request_body);
  }
  
  async function get_scores_by_image_upload() {


    if (file === null){
      return null;
    }

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQuery/";
    
    action_log_without_back_and_forth.push({'method': 'image_upload_query', 'query': 'uploaded image', 'k': max_display_size});
    action_log.push({'method': 'image_upload_query', 'query': 'uploaded image', 'k': max_display_size});

    const params = {
      k: max_display_size,
      add_features : 0,
    };

    const request_body = new FormData();
    request_body.append('image', file);
    request_body.append('query_params', JSON.stringify(params));

    await request_handler(request_url, request_body, false, true);
    
  }

  function dotProduct(vector1, vector2) {
    if (vector1.length !== vector2.length) {
        throw new Error("Vectors must have the same length for dot product computation.");
    }

    let result = 0;
    for (let i = 0; i < vector1.length; i++) {
        result += vector1[i] * vector2[i];
    }

    return result;
  }

  function matrixDotProduct(matrix, vector) {
    if (matrix[0].length !== vector.length) {
        throw new Error("Matrix column count must match the vector length for matrix-vector multiplication.");
    }

    const result = [];
    for (let i = 0; i < matrix.length; i++) {
        const row = matrix[i];
        result.push(dotProduct(row, vector));
    }

    return result;
  }

  // @ts-ignore
  function bayesUpdate() {

    
    if ($selected_images.length == 0){
      return null;
    }

    while(image_items.length > action_pointer + 1){
      image_items.pop();
    }
    
    image_items.push(null);
    action_pointer += 1;
    
    

    let image_items_workcopy = structuredClone(image_items);

    image_items = null;

    let imageFeatureVectors = [];

    for (let i = 0; i < image_items_workcopy.length; i++){
      imageFeatureVectors.push(image_items_workcopy[i].features)
    }

    // Create items array
    var items = Object.keys(image_items_workcopy).map(function(key) {
      return [key, image_items_workcopy[key]];
    });

    let topDisplay = items.slice(0, bayes_display);

    action_log_without_back_and_forth.push({'method': 'bayes', 'query': $selected_images, 'k': topDisplay});
    action_log_pointer +=1;

    action_log.push({'method': 'bayes', 'query': $selected_images, 'k': topDisplay});

    // @ts-ignore
    const negativeExamplesIndices = items.filter(item => !topDisplay.includes(item) && !$selected_images.includes(item));
    const positiveExamplesIndices = items.filter(item => $selected_images.includes(item));

    const negativeExamples = [];
    const positiveExamples = [];

    for (let i = 0; i < negativeExamplesIndices.length; i++){
      negativeExamples.push(imageFeatureVectors[negativeExamplesIndices[i]]);
    }

    for (let i = 0; i < positiveExamplesIndices.length; i++){
      positiveExamples.push(imageFeatureVectors[positiveExamplesIndices[i]]);
    }

    let max_score = 0;

    for (let i = 0; i < image_items_workcopy.length; i++) {
        const featureVector = imageFeatureVectors[i];

        // @ts-ignore
        const PF = negativeExamples.reduce((sum, item) => sum + Math.exp(- (1 - matrixDotProduct(featureVector, positiveExamples)) / alpha), 0);

        // @ts-ignore
        const NF = negativeExamples.reduce((sum, item) => sum + Math.exp(- (1 - matrixDotProduct(featureVector, negativeExamples)) / alpha), 0);

        // @ts-ignore
        image_items_workcopy[i].score = image_items_workcopy[i].score * PF / NF;

        if (image_items_workcopy[i].score > max_score){
          max_score = image_items_workcopy[i].score;
        }
    }

    // Normalization
    for (let i = 0; i < image_items_workcopy.length; i++){
      image_items_workcopy[i].score = image_items_workcopy[i].score/max_score;
    }

    // Create items array
    var items = Object.keys(image_items_workcopy).map(function(key) {
      return [key, image_items_workcopy[key]];
    });

    // Sort the array based on the second element
    items.sort(function(first, second) {
      // @ts-ignore
      return second.score - first.score;
    });

    for (let i = 0; i < items.length; i++){
      // @ts-ignore
      items[i].rank = i;
    }

    image_items = items;

    console.log(image_items);
  }

  function forward_action(){

    if(action_log_without_back_and_forth.length > action_log_pointer){
      action_log_pointer += 1;

      let current = action_log_without_back_and_forth[action_log_pointer-1]
      if (current['method'] == "textquery"){
        lion_text_query = current['query'];

      }else if(current['method'] == "text_filtering"){
        if (!filtered_lables.has(current['label'])){
          filtered_lables.push(current['label']);
          filtered_lables = filtered_lables;
        }

      }else if(current['method'] == "text_restore_filtering"){
        filtered_lables.splice(filtered_lables.indexOf(current['label']), 1);
        filtered_lables = filtered_lables;
      }
      
    }
    
    if (image_items.length - 1 > action_pointer){
      
      if(image_items[action_pointer + 1] === null){
        image_items.pop();
      }else{
        action_pointer += 1;
        image_items = image_items;
        action_log.push({'method': 'forward'});
      }

    }

    handleResize();
  }

  function reset_last(){
    
    if(action_log_pointer > 1){
      action_log_pointer -=1;
    }
    let previous = action_log_without_back_and_forth[action_log_pointer -1];

    if (previous['method'] == "textquery" || previous['method'] == "initialization"){
        lion_text_query = previous['query'];

    }else if(previous['method'] == "text_filtering"){
      if (!filtered_lables.has(previous['label'])){
        filtered_lables.push(previous['label']);
        filtered_lables = filtered_lables;
      }

    }else if(previous['method'] == "text_restore_filtering"){
      filtered_lables.splice(filtered_lables.indexOf(previous['label']), 1);
      filtered_lables = filtered_lables;
    }

    if (image_items.length > 0 && action_pointer > 0){
      action_pointer -= 1;
            
      image_items = image_items;

      action_log.push({'method': 'back'});
    }

    handleResize();
  }

  async function readTextFile(filePath) {
    try {
      const response = await fetch(filePath);
      const data = await response.text();
      return data.split('\n').map(label => label.trim());
    } catch (error) {
      console.error('Error reading text file:', error);
      return [];
    }
  }

  async function findTopNNumbersWithLabels(dictionary, n) {
    const allNumbers = Object.values(dictionary).flatMap(obj => obj.label);
    const numberOccurrences = {};

    // Count occurrences and associate with labels
    allNumbers.forEach(number => {
      const label = file_labels[number];
      numberOccurrences[label] = (numberOccurrences[label] || 0) + 1;
    });

    // Sort the array based on occurrences and then label
    const sortedLabels = Object.keys(numberOccurrences).sort((a, b) => {
      const frequencyComparison = numberOccurrences[b] - numberOccurrences[a];
      if (frequencyComparison !== 0) {
        return frequencyComparison;
      }
      return a.localeCompare(b);
    });

    // Take the top N labels with occurrences
    const topNLabels = sortedLabels.slice(0, n).map(label => ({
      label,
      occurrences: numberOccurrences[label],
      id: file_labels.indexOf(label),
    }));

    return topNLabels;
  }

  function label_click(event){

    const clickedId = event;
    const clickedLabel = file_labels[clickedId];

    console.log(`Clicked bar with label: ${clickedLabel}, Id: ${clickedId}`);
    
    if (filtered_lables.includes(clickedId)){
      // restore disabled items again

      filtered_lables.splice(filtered_lables.indexOf(clickedId), 1);
      filtered_lables = filtered_lables;

      console.log(filtered_lables);

      let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy
      
      if (filtered_lables.length > 0){
        for (const [key, value] of Object.entries(temp_items)) {
          temp_items[key]['disabled'] = true;
        }

        for (const [key, value] of Object.entries(temp_items)) {
          for(let i=0; i < filtered_lables.length; i++){
            if (temp_items[key].label.includes(filtered_lables[i])) {
              temp_items[key]['disabled'] = false;
            }
          }
        }
      }else{
        for (const [key, value] of Object.entries(temp_items)) {
          temp_items[key]['disabled'] = false;
        }
      }
      
      while(image_items.length > action_pointer + 1){
        image_items.pop();
      }

      while(action_log_without_back_and_forth.length > action_log_pointer){
        action_log_without_back_and_forth.splice(action_log_without_back_and_forth.length - 2, 1);
      }
      
      image_items.push(temp_items);

      action_log_without_back_and_forth.push({'method': 'text_restore_filtering', 'label': clickedLabel});
      action_log.push({'method': 'text_restore_filtering', 'label': clickedLabel});

    }else{          
      
      filtered_lables.push(clickedId);
      filtered_lables = filtered_lables;
      
      let num_filtered = 0;

      // Filter out elements in the image_items dictionary that don't contain the clicked label

      let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy

      for (const [key, value] of Object.entries(temp_items)) {
        temp_items[key]['disabled'] = false;
      }

      for (const [key, value] of Object.entries(temp_items)) {
        for(let i=0; i < filtered_lables.length; i++){
          if (!temp_items[key].label.includes(filtered_lables[i])) {
            temp_items[key]['disabled'] = true;
          }
        }
      }
      
      while(image_items.length > action_pointer + 1){
        image_items.pop();
      }

      while(action_log_without_back_and_forth.length > action_log_pointer){
        action_log_without_back_and_forth.splice(action_log_without_back_and_forth.length - 2, 1);
      }

      image_items.push(temp_items);
      
      action_log_without_back_and_forth.push({'method': 'text_filtering', 'label': clickedLabel, 'num_filtered': num_filtered});
      action_log.push({'method': 'text_filtering', 'label': clickedLabel, 'num_filtered': num_filtered});

    }
    
    action_pointer += 1;
    action_log_pointer += 1;

    console.log(image_items[action_pointer]);

    handleResize();

    
  }

  // @ts-ignore
  async function create_chart(){
    if (image_items[action_pointer][0] != null && image_items[action_pointer][0]['label'] != null){
      
      // remove disabled items
      let temp_items = {};

      console.log("Start");
      console.log(filtered_lables);
      console.log(image_items[action_pointer]);

      for (let i = 0; i < image_items[action_pointer].length; i++) {
        if (image_items[action_pointer][i].hasOwnProperty('disabled') && !image_items[action_pointer][i]['disabled']) {
          temp_items[i] = image_items[action_pointer][i]
        }else if(image_items[action_pointer][i].hasOwnProperty('disabled') && image_items[action_pointer][i]['disabled']){
          // do nothing
        }else{
          temp_items[i] = image_items[action_pointer][i]
        }
      }

      temp_items = Object.values(temp_items);
      
      console.log(temp_items);
      console.log("END");

      const topNumbersWithOccurrences = await findTopNNumbersWithLabels(temp_items, 7);

      allLabels = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.label);
      allOccurrences = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.occurrences);
      allIds = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.id);

      console.log(allLabels);
      let border_colors = [];

      for(let i=0; i < allIds.length; i++){
        if (filtered_lables.includes(allIds[i])) {
          border_colors.push('#FF0000');
        }else{
          border_colors.push('rgba(0, 0, 0, 0.0)');
        }
      }

      // @ts-ignore

      const canvas = document.getElementById('myChart');

      // clear previous canvas
      var new_canvas = document.createElement("canvas");
      new_canvas.setAttribute("id", "myChart");
      new_canvas.setAttribute("class", "menu_item");
      new_canvas.setAttribute("style", "width:300px;height:300px");
      canvas.replaceWith(new_canvas)

      const ctx = document.getElementById('myChart').getContext('2d'); // 2d context

      // @ts-ignore
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: allLabels,
          datasets: [{
            label: 'Display Clusters',
            borderColor: border_colors,
            borderWidth: 3,
            backgroundColor: [
              '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', '#ffffff', '#000000'
            ],
            data: allOccurrences
          }]
        },
        options: {
          onClick: function (event, elements) {
            if (elements.length > 0) {
              // Get the index of the clicked bar
              const clickedIndex = elements[0]._index;

              const clickedLabel = allLabels[clickedIndex];
              const clickedOccurrence = allOccurrences[clickedIndex];
              const clickedId = allIds[clickedIndex];

              console.log(`Clicked bar with label: ${clickedLabel}, Id: ${clickedId}`);
              
              if (filtered_lables.includes(clickedId)){
                // restore disabled items again

                filtered_lables.splice(filtered_lables.indexOf(clickedId), 1);
                filtered_lables = filtered_lables;

                console.log(filtered_lables);

                let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy
                
                if (filtered_lables.length > 0){
                  for (const [key, value] of Object.entries(temp_items)) {
                    temp_items[key]['disabled'] = true;
                  }

                  for (const [key, value] of Object.entries(temp_items)) {
                    for(let i=0; i < filtered_lables.length; i++){
                      if (temp_items[key].label.includes(filtered_lables[i])) {
                        temp_items[key]['disabled'] = false;
                      }
                    }
                  }
                }else{
                  for (const [key, value] of Object.entries(temp_items)) {
                    temp_items[key]['disabled'] = false;
                  }
                }
                
                while(image_items.length > action_pointer + 1){
                  image_items.pop();
                }

                while(action_log_without_back_and_forth.length > action_log_pointer){
                  action_log_without_back_and_forth.splice(action_log_without_back_and_forth.length - 2, 1);
                }
                
                image_items.push(temp_items);

                action_log_without_back_and_forth.push({'method': 'text_restore_filtering', 'label': clickedLabel});
                action_log.push({'method': 'text_restore_filtering', 'label': clickedLabel});

              }else{          
                
                filtered_lables.push(clickedId);
                filtered_lables = filtered_lables;
                
                let num_filtered = 0;

                // Filter out elements in the image_items dictionary that don't contain the clicked label

                let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy

                for (const [key, value] of Object.entries(temp_items)) {
                  temp_items[key]['disabled'] = false;
                }

                for (const [key, value] of Object.entries(temp_items)) {
                  for(let i=0; i < filtered_lables.length; i++){
                    if (!temp_items[key].label.includes(filtered_lables[i])) {
                      temp_items[key]['disabled'] = true;
                    }
                  }
                }
                
                while(image_items.length > action_pointer + 1){
                  image_items.pop();
                }

                while(action_log_without_back_and_forth.length > action_log_pointer){
                  action_log_without_back_and_forth.splice(action_log_without_back_and_forth.length - 2, 1);
                }

                image_items.push(temp_items);
                
                action_log_without_back_and_forth.push({'method': 'text_filtering', 'label': clickedLabel, 'num_filtered': num_filtered});
                action_log.push({'method': 'text_filtering', 'label': clickedLabel, 'num_filtered': num_filtered});

              }
              
              action_pointer += 1;
              action_log_pointer += 1;

              console.log(image_items[action_pointer]);

              handleResize();

            }
          },
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero: true,
                callback: function(value) {if (value % 1 === 0) {return value;}}
              },
            }]
          }  
        },
      });
    }   
  }

</script>

<main>
  <div class='viewbox'>
    <div class='top-menu'>
      <div class="top-input">
        <input class="top-menu-item resize-text top-offset" bind:value={username} placeholder="Your username"/>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select bind:value_dataset label="Select Dataset">
          {#each datasets as dataset}
            <Option value={dataset}>{dataset}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select bind:value_model label="Select Model">
          {#each models as model}
            <Option value={model}>{model}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset3">
        <Button color="primary" on:click={send_results_multiple} variant="raised">
          <span class="resize-text">Send Selected Images</span>
        </Button>
      </div>
      <div class="top-input">
        <input class="top-menu-item resize-text top-offset" bind:value={custom_result} placeholder="Your custom result message"/>
      </div>
      <div class ="top-menu-item top-negative-offset3" >
        <Button color="primary" on:click={send_results_custom} variant="raised">
          <span class="resize-text">Send custom text</span>
        </Button> 
      </div>
      
    </div>

    <div class="horizontal">
      <div class='menu'>
        <div class='buttons'>
          <div class="centering" style="margin-bottom:0.5em;">
            <Fab on:click={reset_last} extended ripple={false}>
              <Icon class="material-icons">arrow_back</Icon>
            </Fab>
            <Fab on:click={forward_action} extended ripple={false}>
              <Icon class="material-icons">arrow_forward</Icon>
            </Fab>
          </div>
          {#if send_results.length > 0}
            <span>Your send results: {send_results}</span>
          {/if}
          <div class="timer centering" style="margin-bottom:0.5em;">
            <Timer bind:this={timer}/>
          </div>
          <Button class="menu_item menu_button" color="secondary" on:click={get_test_image} variant="raised">
            <span class="resize-text">Random Test Image</span>
          </Button>
          {#if true}
            <div id="test-image-preview-container">
              <img id="testimage" alt="" />
            </div>
          {/if}
          <input class="menu_item resize-text" bind:value={lion_text_query} placeholder="Your text query" on:keypress={handleKeypress}/>
          <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_text} variant="raised">
            <span class="resize-text">Submit Text Query</span>
          </Button>
          <div class="filedrop-container menu_item">
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div class="file-drop-area menu_item" on:dragenter={noopHandler} on:dragexit={noopHandler} on:dragover={noopHandler} on:drop={drop}>
              <span class="fake-btn">Choose files</span>
              <span class="file-msg">or drag and drop file here</span>
              <input class="file-input" type="file">
            </div>
            {#if dragged_url != null}
              <div class="image-preview-container menu_item">
                <img class="preview_image" alt="preview upload" src={dragged_url}/>
              </div>
            {/if}
          </div>
          <Button class="menu_item menu_button" color="secondary" on:click={bayesUpdate} variant="raised">
            <span class="resize-text">Bayes Update</span>
          </Button>
          <canvas class="menu_item" id="myChart" style="width:300px;height:300px;"></canvas>
          {#key filtered_lables}
            {#if filtered_lables.length > 0}
              <p >Active label filter</p>
            {/if}
            {#each filtered_lables as label}
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
              <p class='active_label' on:click={() => label_click(label)}>{file_labels[label]}</p>
            {/each}
          {/key}
          <Button class="menu_item menu_button" color="secondary" on:click={download_results} variant="raised">
            <span class="resize-text">Download Test Data</span>
          </Button>
        </div>
      </div>
      {#key image_items}
        {#key prepared_display}
          <div id='container'>
            {#if prepared_display === null}
              <p>...loading</p>
            {:else}
              {#await prepared_display}
                <p>...loading</p>
              {:then prepared_display}             
                <VirtualList items={prepared_display} bind:start bind:end let:item>
                  <ImageList on:send_result={send_results_single} on:similarimage={get_scores_by_image} on:video_images={video_images} row={item} bind:row_size/>
                </VirtualList>
                <p>showing image rows {start}-{end}. Total Rows: {prepared_display.length} - Total Images:  {prepared_display.reduce((count, current) => count + current.length, 0)}</p>
              {/await}
            {/if}
          </div>
        {/key}
      {/key}
    </div>
  </div>
</main>

<style>

.active_label{
  color: red;
  text-align: left;
  margin-left: 2em;
  margin-right: 2em;
  padding: 0.5em;
  background-color: lightgray;
  cursor: pointer;
}

#myChart{
  width: auto;
}

.centering{
  display: flex;
  flex-direction: row;
  justify-content: center; /* Center items horizontally */
  width: 100%;
}

.horizontal{
  display: flex; /* Create a new flex container for the two bottom elements */
  flex: 1;
}
.resize-text{
  font-size: 0.75em;
}

.file-drop-area {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  border: 1px dashed rgba(61, 61, 61, 0.4);
  border-radius: 3px;
  transition: 0.2s;
  &.is-active {
    background-color: rgba(255, 255, 255, 0.05);
  }
}

.top-menu{
  flex: 1;
  display: flex;
}

.top-menu-item{
  display: flex;
  margin-left: 1em;
  margin-bottom: 0.25em;
}

.top-offset{
  margin-top: 1.25em;
}

.top-input{
  height: 100%;
}


.fake-btn {
  flex-shrink: 0;
  background-color: rgba(54, 53, 53, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.1em;
  padding: 0.2em 0.4em;
  margin-right: 0.25em;
  font-size: 0.75em;
  text-transform: uppercase;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.file-msg {
  font-size: 0.75em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-input {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 100%;
  cursor: pointer;
  opacity: 0;
  &:focus {
    outline: none;
  }
}

#container {
  min-height: 200px;
  height: calc(100vh - 7.0em);
  width: 85%;
  float: left;
  background-color: rgb(202, 202, 202);
}

.filedrop-container{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 90%;
}

.image-preview-container{
  width: 100%;
  height: 6em;
  display: block;
}

.preview_image{
  height: 100%;
  width: 100%;
  object-fit: contain;
}

#testimage{
  height: 100%;
  width: 100%;
  object-fit: contain;
}

.top-negative-offset{
  margin-top: -1.5em;
}

.top-negative-offset3{
  margin-top: -0.2em;
}

</style>
