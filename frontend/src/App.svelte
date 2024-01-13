<script>
// @ts-nocheck

  import { selected_images, scroll_height, in_video_view } from './stores.js';
  import ImageList from './ImageList.svelte';

  import Timer from './Timer.svelte';

  import VirtualList from './VirtualListNew.svelte';
  
  import Button from '@smui/button';

  import Select, { Option } from '@smui/select';
  
  import Fab, { Icon } from '@smui/fab';

  import { onMount, onDestroy, tick} from 'svelte';


  let timer;

  let lion_text_query = "";

  let start;
	let end;
  let image_items = [];
  let alpha = 0.1;

  let custom_result = "";

  let max_display_size = 1000;

  let chart_labels = 15;

  let test_image_av = false;

  let row_size;
  let prepared_display = null;

  $: {
    //reloading_display(image_items);
    set_scroll($scroll_height);
    prepared_display;
    filtered_lables;
  }

  let random_target = null;

  let datasets = ['V3C', 'mvk', 'Medical'];

  let models = ['clip-laion', 'clip-openai'];

  let users = ['PraK1', 'PraK2', 'PraK3', 'PraK4', 'PraK5'];

  let passwords = ['G5L>q:e{', 't+6^y%T[', 'K}84dH/`', 'Lq&9Mc6Z', 'gb~.8mMy'];
 
  let value_dataset = 'V3C';

  let value_model = 'clip-laion';

  let username = "PraK1";

  let send_results = "";

  let action_log = [];

  let action_log_without_back_and_forth = [];
  let action_log_pointer = -1;

  let bayes_display = max_display_size;

  let dragged_url = null;

  let action_pointer = -1;

  let file = null;

  let allLabels = [];

  let allOccurrences = [];

  let allIds = [];

  let filtered_lables = [];

  let file_labels = [];

  let labelColorMap = {};

  let target_in_display_text = "Target is not in current Display!";
  let target_in_display = false;

  let image_from_target_video_in_display = false;
  
  let virtual_list;

  let current_action_pointer = -1;

  let session_id;

  let servertime;

  initialization();

  get_session_id_for_user();

  async function handle_submission(video, frame, text=''){

    let synchtime = await getSyncedServerTime();
    let request_url;

    if (text != ''){
      request_url = "https://vbs.videobrowsing.org:443/api/v1/submit/?item=" + video + "&text=" + text + "&frame=" + frame + "&session=" + session_id;
    }else{
      request_url = "https://vbs.videobrowsing.org:443/api/v1/submit/?item=" + video + "&frame=" + frame + "&session=" + session_id;
    }
    

    console.log(request_url);

    let response = await fetch(request_url, {
      method: 'GET',
      headers: {
        'Content-Type': 'text'
      },
    });

    if (response.ok) { 
      
      let res = await response.text()
      console.log('Successfully submitted result to DRES server!');
    }

    /*request_url = "https://vbs.videobrowsing.org:443/api/v2/submit/VBS2024Test";

    console.log(request_url);
    
    let request_body = JSON.stringify({
        item: '12791',
        frame: '1',
        session: session_id,
        evaluationId: 'VBS2024Test',
    });

    response = await fetch(request_url, {
      method: 'POST',
      session: session_id,
      evaluationId: 'VBS2024Test',
      headers: {
        'Content-Type': 'application/json'
      },
      body: request_body
    });

    if (response.ok) {

      res = await response.json();

      console.log(res);

    }*/
  }

  async function getSyncedServerTime() {
    // Get current timestamp in milliseconds
    const clientTimestamp = new Date().getTime();

    const response = await fetch('https://vbs.videobrowsing.org:443/api/v2/status/time', {
        method: 'GET',
    });

    if (response.ok) {

      let res = await response.json();

      const serverTimestamp = res['timeStamp'];

      // Get current timestamp in milliseconds
      const nowTimeStamp = new Date().getTime();

      // Calculate server-client difference time on response and response time
      const serverClientResponseDiffTime = nowTimeStamp - serverTimestamp;
      const responseTime = (clientTimestamp - serverTimestamp - nowTimeStamp + clientTimestamp - serverClientResponseDiffTime ) / 2;

      // Calculate the synced server time
      const syncedServerTime = new Date(nowTimeStamp + (serverClientResponseDiffTime - responseTime));

      return syncedServerTime;
    }else{
      return null;
    }

  }
  async function get_session_id_for_user(){

    let request_url = "https://vbs.videobrowsing.org:443/api/v2/login";

    let request_body = JSON.stringify({
        username: username,
        password: passwords[users.indexOf(username)],
    });
    
    let response = await fetch(request_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: request_body
    });

    if (response.ok) {

      let res = await response.json();

      session_id = res['sessionId'];

      console.log(session_id);
    }else{
      console.log(response);
    }
  }

  function set_scroll(scroll){
    if (action_log[action_log_pointer] != null){
      action_log[action_log_pointer]['scroll'] = $scroll_height;
    }
  }
 
  function arrayEquals(a, b) {
    return Array.isArray(a) &&
        Array.isArray(b) &&
        a.length === b.length &&
        a.every((val, index) => val === b[index]);
  }

  function scrollToHeight(height) {
    setTimeout(function(){
      if(virtual_list){
        virtual_list.scrollToScrollHeight(height, { behavior: 'auto' });

        virtual_list.handle_scroll();
      }
    }, 50);


  }

  function scroll_to_index(index) {
    setTimeout(function(){
      if(virtual_list){
        virtual_list.scrollToIndex(index, { behavior: 'auto' });
        
        virtual_list.handle_scroll();
      }
    }, 50);
  }

  async function reloading_display(video_image_id=0){

    start = 0;
    const previous_btn = document.getElementById("previous");

    if(action_log_pointer <= 0){
      previous_btn.style.backgroundColor = "lightgrey";
      previous_btn.style.cursor = "default";
    }else{
      previous_btn.style.backgroundColor = "grey";
      previous_btn.style.cursor = "pointer";
    }
  
    const next_btn = document.getElementById("next");

    if(action_log.length - 1 <= action_log_pointer){
      next_btn.style.backgroundColor = "lightgrey";
      next_btn.style.cursor = "default";
    }else{
      next_btn.style.backgroundColor = "grey";
      next_btn.style.cursor = "pointer";
    }
    
    if(image_items[action_pointer] != null){

      if(action_log[action_log_pointer]['method'] == 'show_video_frames'){
        $in_video_view = true;
      }else{
        $in_video_view = false;
      }

      if(action_log[action_log_pointer]['method'] == 'textquery'){
        lion_text_query = action_log[action_log_pointer]['query'];
      }else{
        lion_text_query = '';
      }

      row_size = Math.floor(window.innerWidth / 550);

      bayes_display = max_display_size;
      
      console.log("reloading display");

      let rows = [];
      let row = -1;

      let s = 0;

      target_in_display = false;

      image_from_target_video_in_display = false;

      let temp_selection = [];

      let scroll_index;

      for (let i = 0; i < image_items[action_pointer].length; i++) {

        if (action_log[action_log.length - 1]['method'] == "show_video_frames" && video_image_id != 0){
            
          if (image_items[action_pointer][i]['id'][0] == video_image_id[0] && image_items[action_pointer][i]['id'][1] == video_image_id[1]){
            scroll_index = rows.length;
          }
        }

        if (random_target != null && arrayEquals(image_items[action_pointer][i]['id'], random_target[0]['id'])){
          target_in_display = true;
          image_from_target_video_in_display = true;
        }else if (random_target != null && image_items[action_pointer][i]['id'][0] == random_target[0]['id'][0]){
          image_from_target_video_in_display = true;
        }

        if(image_items[action_pointer][i]['id'] in $selected_images){
          temp_selection.push(image_items[action_pointer][i]['id']);
        }

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

      $selected_images = temp_selection;

      if (target_in_display && random_target != null ){
        target_in_display_text = "Target in current Display!"
      }else if(image_from_target_video_in_display && random_target != null){
        target_in_display_text = "Image from target video in current Display, but not the target!"
      }else if(random_target != null){
        target_in_display_text = "No image from target video in current Display!";
      }else{
        target_in_display_text = "Currently no Target."
      }

      prepared_display = rows;

      
      if (action_log[action_log.length - 1]['method'] == "show_video_frames" && video_image_id != 0 && scroll_index != undefined){
        scroll_to_index(scroll_index);
      }


      create_chart();

    }else{
      prepared_display = null;
    }

    console.log(prepared_display);

  }

  onMount(() => {
    window.addEventListener('resize', reloading_display);    
    return () => {
      window.removeEventListener('resize', reloading_display);
    };
  });

  function noopHandler(evt) {
      evt.preventDefault();
  }
  
  function drop(evt) {

    evt.preventDefault();
    file = evt.dataTransfer.files[0];

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

    action_log.push({'method': 'send_custom_result', 'result_items': send_results});

    handle_submission(null, null, send_results);
  }

  function send_results_single(event){
    timer.stop();

    send_results = event.detail.image_id;

    $selected_images = [];

    action_log.push({'method': 'send_single_result', 'result_items': send_results});

    handle_submission(send_results[0], send_results[1]);
  }

  function send_results_multiple(){
    timer.stop();

    send_results = " ";

    $selected_images.forEach((selection) => {
      send_results += `${selection}; `;
    });

    send_results = send_results.slice(0, -2); // remove last space and semicolon

    $selected_images = [];

    action_log.push({'method': 'send_multi_result', 'result_items': send_results});
  }

  function download(content, fileName, contentType) {
      var a = document.createElement("a");
      var file = new Blob([content], {type: contentType});
      a.href = URL.createObjectURL(file);
      a.download = fileName;
      a.click();
  }

  function download_results(){
    let full_data;

    if (random_target != null){
      const target = {'target': random_target[0]['id']};
      full_data = [target].concat(action_log);
    }else{
      full_data = action_log
    }

    console.log(full_data);

    var action_log_json = JSON.stringify(full_data);

    download(action_log_json, 'action_log.txt', 'text/plain');

  }

  async function get_test_image(){

    image_items = [];
    action_log = [];

    action_pointer = -1;

    action_log_pointer = -1;

    initialization();

  
    //$selected_images.forEach((selection) => {
    //  send_results += `${selection}; `;
    //});
    
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

    action_log.push({'method': 'show_video_frames', 'query': [selected_item[0], selected_item[1]]});

    const request_body = JSON.stringify({
      item_id: String(selected_item[0]) + "_" + String(selected_item[1]),
      k: -1,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
    });

    request_handler(request_url, request_body, false, false, selected_item);
    
  }

  async function initialization() {

    // Read labels from the text file
    file_labels = await readTextFile('./assets/nounlist.txt');

    
    // setting this to null temporarily will make a loading display to appear
    prepared_display = null;

    action_log.push({'method': 'initialization', 'query': '', 'k': 50});
    
    const request_url = "http://acheron.ms.mff.cuni.cz:42032/getVideoFrames/";

    try {
        const response = await fetch("http://acheron.ms.mff.cuni.cz:42032/getRandomFrame/");
        if (response.ok) {

          let init = await response.json();

          let init_id = init[0]["id"];

          const request_body = JSON.stringify({
            item_id: String(init_id[0]) + "_" + String(init_id[1]),
            k: -1,
            dataset: value_dataset,
            add_features: 1,
            speed_up: 1,
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

  async function request_handler(request_url, request_body, init=false, image_upload=false, video_image_id=0){

    // action log got a new entry in function that called the request_handler. We increment here have less code
    action_log_pointer += 1;

    // setting this to null temporarily will make a loading display to appear
    prepared_display = null;


    // unwind actions after backtracking
    while(image_items.length -1 > action_pointer){
      image_items.pop();
    }

    while(action_log.length -1 > action_log_pointer){
      // remove the second to last elements because we newly added the last before the request_handler
      action_log.splice(action_log.length - 2, 1);
    }

    action_pointer += 1;

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

      if (action_log.length - 1 >= 0){
        // insert the data to the action we performed before calling the requesthandler
        action_log[action_log.length - 1]['data'] = image_items[action_pointer];
      }
      
      // reset the selection
      $selected_images = [];
      
      if (video_image_id != 0){
        reloading_display(video_image_id);
      }else{
        reloading_display();
      }
      

    } catch (error) {
      console.error(error);
    }

  }

  async function get_scores_by_text() {

    action_log_without_back_and_forth.push({'method': 'textquery', 'query': lion_text_query});
    action_log.push({'method': 'textquery', 'query': lion_text_query});

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/textQuery/";

    const request_body = JSON.stringify({
      query: lion_text_query,
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
    });

    await request_handler(request_url, request_body);
  }

  async function get_scores_by_image(event) {

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQueryByID/";

    let selected_item = event.detail.image_id;

    action_log_without_back_and_forth.push({'method': 'image_internal_query', 'query': [selected_item[0], selected_item[1]]});

    action_log.push({'method': 'image_internal_query', 'query': [selected_item[0], selected_item[1]]});

    const request_body = JSON.stringify({
      video_id: selected_item[0],
      frame_id: selected_item[1],
      k: max_display_size,
      dataset: value_dataset,
      add_features: 1,
      speed_up: 1,
    });

    await request_handler(request_url, request_body);
  }
  
  async function get_scores_by_image_upload() {


    if (file === null){
      return null;
    }

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQuery/";
    
    action_log_without_back_and_forth.push({'method': 'image_upload_query', 'query': 'uploaded image'});
    action_log.push({'method': 'image_upload_query', 'query': 'uploaded image'});

    const params = {
      k: max_display_size,
      add_features: 1,
      dataset: value_dataset,
      speed_up: 1,
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

  function normalizeVector(vector) {
    const norm = Math.sqrt(vector.reduce((sum, value) => sum + value ** 2, 0));

    // Check for division by zero or zero vector
    if (norm === 0 || isNaN(norm)) {
        return vector.map(value => 0); // Return a vector of zeros
    }

    return vector.map(value => value / norm);
  }

  function normalizeMatrix(matrix) {
      return matrix.map(row => normalizeVector(row));
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

  function bayesUpdate() {
    
    if ($selected_images.length == 0){
      console.log("Nothing was selected. Cannot perform the Bayes update without a positve example.");
      return null;
    }

    if(!image_items[action_pointer][0].hasOwnProperty('score')){
      console.log("No Score to compare images with. Please initialize them with a query!");
      return null;
    }

    // unwind actions after backtracking
    while(image_items.length -1 > action_pointer){
      image_items.pop();
    }

    while(action_log.length -1 > action_log_pointer){
      // remove the second to last elements because we newly added the last before the request_handler
      action_log.splice(action_log.length - 2, 1);
    }

    let DeepCopyImageItems = structuredClone(image_items[action_pointer]);
    
    let imageFeatureVectors = [];

    for (let i = 0; i < image_items[action_pointer].length; i++){
      imageFeatureVectors.push(image_items[action_pointer][i].features);
    }

    // Create items array format so we can filter

    var items = Object.keys(image_items[action_pointer]).map(function(key) {
      return image_items[action_pointer][key];
    });
    
    let topDisplay = items.slice(0, Math.min(items.length, bayes_display));

    let negativeExamples = topDisplay.filter(item =>
      !$selected_images.some(selectedImage =>
        selectedImage[0] === item.id[0] && selectedImage[1] === item.id[1]
      )
    ).map(filteredItem => filteredItem.features);

    let positiveExamples = items
    .filter(item =>
      $selected_images.some(selectedImage =>
        selectedImage[0] === item.id[0] && selectedImage[1] === item.id[1]
      )
    )
    .map(filteredItem => filteredItem.features);

    positiveExamples = normalizeMatrix(positiveExamples);
    negativeExamples = normalizeMatrix(negativeExamples);

    let prod;
    let PF;
    let NF;
    let featureVector;

    for (let i = 0; i < items.length; i++) {
        featureVector = imageFeatureVectors[i];
        
        prod = matrixDotProduct(positiveExamples, normalizeVector(featureVector));

        if (prod.length > 1){
          PF = prod.reduce((partialSum, a) => partialSum +  Math.exp(- (1 - a) / alpha), 0); // sum array
        }else{
          PF = Math.exp(- (1 - prod[0]) / alpha)
        }
        
        prod = matrixDotProduct(negativeExamples, normalizeVector(featureVector))

        if (prod.length > 1){
          NF = prod.reduce((partialSum, a) => partialSum +  Math.exp(- (1 - a) / alpha), 0); // sum array
        }

        DeepCopyImageItems[i].score = DeepCopyImageItems[i].score * PF / NF;        
    }

    // Create items array
    var items = Object.keys(DeepCopyImageItems).map(function(key) {
      return DeepCopyImageItems[key];
    });

    // Sort the array based on the second element
    items.sort(function(first, second) {
      return second.score - first.score;
    });

    for (let i = 0; i < items.length; i++){
      items[i].rank = i;
    }

    image_items.push(items);

    action_pointer += 1;

    action_log.push({'method': 'bayes_update', 'selected_video_image_ids': $selected_images, 'display': topDisplay, 'data': image_items[action_pointer]});

    action_log_pointer += 1;
    reloading_display();

    scrollToHeight(0);
  }

  function traverse_states(a){

    // no action when we are at the initialization or there is no next action yet.
    if(a == -1 && action_log_pointer <= 0){
      return null;
    }else if(a == 1 && action_log.length - 1 <= action_log_pointer){
      return null;
    }

    if(a == -1){
      // current state before taking action
      let display_state = action_log[action_log_pointer];

      if(display_state['method'] == "text_filtering"){
        filtered_lables.splice(filtered_lables.indexOf(display_state['label']), 1);
      }else if(display_state['method'] == "text_restore_filtering"){
        if (!filtered_lables.includes(display_state['label'])){
          filtered_lables.push(display_state['label']);
        }
      }
    }else{
      // state after taking action
      let after_state = action_log[action_log_pointer + a];

      if(after_state['method'] == "text_filtering"){
        if (!filtered_lables.includes(after_state['label'])){
          filtered_lables.push(after_state['label']);
        }
      }else if(after_state['method'] == "text_restore_filtering"){
        filtered_lables.splice(filtered_lables.indexOf(after_state['label']), 1);
      }
    }

    // trigger reload of labels under chart
    filtered_lables = filtered_lables;

    // will be decreased if action is -1 and increased if action is + 1
    action_log_pointer = action_log_pointer + a;
    action_pointer = action_pointer + a;

    reloading_display();

    // will be previous if action is -1 and next if action is + 1
    scrollToHeight(action_log[action_log_pointer]['scroll']);

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

      let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy
      
      if (filtered_lables.length > 0){
        for (const [key, value] of Object.entries(temp_items)) {
          temp_items[key]['disabled'] = true;
        }

        let one_not_included = false;
        for (const [key, value] of Object.entries(temp_items)) {
          one_not_included = false;

          for(let i=0; i < filtered_lables.length; i++){
            if (!temp_items[key].label.includes(filtered_lables[i])) {
              one_not_included = true;
            } 
          }
          if(!one_not_included){
            temp_items[key]['disabled'] = false;
          }
        }
        
      }else{
        for (const [key, value] of Object.entries(temp_items)) {
          temp_items[key]['disabled'] = false;
        }
      }
      
      // unwind actions after backtracking
      while(image_items.length -1 > action_pointer){
        image_items.pop();
      }

      while(action_log.length -1 > action_log_pointer){
        // remove the second to last elements because we newly added the last before the request_handler
        action_log.splice(action_log.length - 2, 1);
      }
      
      image_items.push(temp_items);
      
      action_log.push({'method': 'text_restore_filtering', 'label': clickedId, 'data': image_items[action_pointer]});

    }else{          
      
      filtered_lables.push(clickedId);
      
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
      
      // unwind actions after backtracking
      while(image_items.length -1 > action_pointer){
        image_items.pop();
      }

      while(action_log.length -1 > action_log_pointer){
        // remove the second to last elements because we newly added the last before the request_handler
        action_log.splice(action_log.length - 2, 1);
      }

      image_items.push(temp_items);
      
      action_log.push({'method': 'text_filtering', 'label': clickedId, 'num_filtered': num_filtered, 'data': image_items[action_pointer]});

    }

    // trigger reload of labels under chart
    filtered_lables = filtered_lables;
    
    action_pointer += 1;
    action_log_pointer += 1;

    reloading_display();

    
  }

  function generateColor(label) {
    // Check if the label already has a color assigned
    if (!labelColorMap[label]) {
      // Generate a random color for the label
      var r = Math.floor(Math.random() * 256);
      var g = Math.floor(Math.random() * 256);
      var b = Math.floor(Math.random() * 256);

      // Mix with white to create a pastel effect
      var mixColor = 255; // White color
      r = Math.floor((r + mixColor) / 2);
      g = Math.floor((g + mixColor) / 2);
      b = Math.floor((b + mixColor) / 2);

      labelColorMap[label] = 'rgba(' + r + ',' + g + ',' + b + ', 1.0)';
    }

    return labelColorMap[label];
  }

  async function create_chart(){
    if (image_items[action_pointer][0] != null && image_items[action_pointer][0]['label'] != null){
      
      // remove disabled items
      let temp_items = {};
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


      const topNumbersWithOccurrences = await findTopNNumbersWithLabels(temp_items, chart_labels);

      allLabels = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.label);
      allOccurrences = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.occurrences);
      allIds = Object.values(topNumbersWithOccurrences).flatMap(obj => obj.id);

      let border_colors = [];

      for(let i=0; i < allIds.length; i++){
        if (filtered_lables.includes(allIds[i])) {
          border_colors.push('#FF0000');
        }else{
          border_colors.push('rgba(0, 0, 0, 0.0)');
        }
      }


      const canvas = document.getElementById('myChart');

      // clear previous canvas
      let new_canvas = document.createElement("canvas");
      new_canvas.setAttribute("id", "myChart");
      new_canvas.setAttribute("class", "menu_item");
      new_canvas.setAttribute("style", "margin-left: 2em; margin-right: 2em;  height: 30em");
      canvas.replaceWith(new_canvas)

      const ctx = document.getElementById('myChart').getContext('2d'); // 2d context

      let myHorizontalBarChart = new Chart(ctx, {
        type: "bar",
        data: {
          
          labels: allLabels,
          datasets: [{
            label: 'Display Clusters',
            borderColor: border_colors,
            borderWidth: 3,
            data: allOccurrences
          }]
        },
        options: {
          onClick: function (event, elements) {
            if (elements && elements.length > 0) {
              
              // Get the index of the clicked bar
              const clickedIndex = elements[0].index;

              const clickedLabel = allLabels[clickedIndex];
              const clickedOccurrence = allOccurrences[clickedIndex];
              const clickedId = allIds[clickedIndex];

              console.log(`Clicked bar with label: ${clickedLabel}, Id: ${clickedId}`);
              
              if (filtered_lables.includes(clickedId)){
                // restore disabled items again

                filtered_lables.splice(filtered_lables.indexOf(clickedId), 1);
                filtered_lables = filtered_lables;

                let temp_items = window.structuredClone(image_items[action_pointer]); // deepcopy
                
                if (filtered_lables.length > 0){
                  for (const [key, value] of Object.entries(temp_items)) {
                    temp_items[key]['disabled'] = true;
                  }
                  
                  let one_not_included = false;

                  for (const [key, value] of Object.entries(temp_items)) {
                    one_not_included = false;

                    for(let i=0; i < filtered_lables.length; i++){
                      if (!temp_items[key].label.includes(filtered_lables[i])) {
                        one_not_included = true;
                      } 
                    }
                    if(!one_not_included){
                      temp_items[key]['disabled'] = false;
                    }
                  }

                }else{
                  for (const [key, value] of Object.entries(temp_items)) {
                    temp_items[key]['disabled'] = false;
                  }
                }
                
                // unwind actions after backtracking
                while(image_items.length -1 > action_pointer){
                  image_items.pop();
                }

                while(action_log.length -1 > action_log_pointer){
                  // remove the second to last elements because we newly added the last before the request_handler
                  action_log.splice(action_log.length - 2, 1);
                }
                
                image_items.push(temp_items);

                action_log.push({'method': 'text_restore_filtering', 'label': clickedId, 'data': image_items[action_pointer]});

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
                
                // unwind actions after backtracking
                while(image_items.length -1 > action_pointer){
                  image_items.pop();
                }

                while(action_log.length -1 > action_log_pointer){
                  // remove the second to last elements because we newly added the last before the request_handler
                  action_log.splice(action_log.length - 2, 1);
                }

                image_items.push(temp_items);
                
                action_log.push({'method': 'text_filtering', 'label': clickedId, 'num_filtered': num_filtered, 'data': image_items[action_pointer]});

              }
              
              action_pointer += 1;
              action_log_pointer += 1;

              reloading_display();

            }
          },
          indexAxis: 'y',
          scales: {
            x: {
              beginAtZero: true
            },
            y: {
              position: 'left',
              reverse: false,
              callback: function(value) {if (value % 1 === 0) {return value;}}
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return context.dataset.data[context.dataIndex];
                }
              }
            }
          }
        },
      });

      // Dynamically assign colors based on labels
      myHorizontalBarChart.data.datasets[0].backgroundColor = myHorizontalBarChart.data.labels.map(generateColor);
      myHorizontalBarChart.update(); // Update the chart
      
    }   
  }

</script>

<main>
  <div class='viewbox'>
    <div class='top-menu'>
      <div class="top-menu-item top-negative-offset">
        <Select on:SMUISelect:change={get_session_id_for_user} bind:value={username} label="Select User">
          {#each users as user}
            <Option value={user}>{user}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select bind:value={value_dataset} label="Select Dataset">
          {#each datasets as dataset}
            <Option value={dataset}>{dataset}</Option>
          {/each}
        </Select>
      </div>
      <div class="top-menu-item top-negative-offset">
        <Select bind:value={value_model} label="Select Model">
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
        <span class="top-menu-item" id="target_text">{target_in_display_text}</span>
    </div>

    <div class="horizontal">
      <div class='menu'>
        <br>
        <div class='buttons'>
          <div class="centering" style="margin-bottom:0.5em;">
            <Fab id="previous" on:click={() => traverse_states(-1)} extended ripple={false}>
              <Icon style="font-size:20px;" class="material-icons">arrow_back</Icon>
            </Fab>
            <Fab id="next" on:click={() => traverse_states(1)} extended ripple={false}>
              <Icon style="font-size:20px;" class="material-icons">arrow_forward</Icon>
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
          <textarea  id="text_query_input" class="menu_item resize-text" bind:value={lion_text_query} placeholder="Your text query" on:keypress={handleKeypress}/>
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
          <canvas class="menu_item" id="myChart"></canvas>
          <div id="customLegend" class="menu_item" ></div>
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
          <div id='container'>
            {#if prepared_display === null}
              <p>...loading</p>
            {:else}           
              <VirtualList items={prepared_display} bind:this={virtual_list} bind:start bind:end let:item>
                <ImageList on:send_result={send_results_single} on:similarimage={get_scores_by_image} on:video_images={video_images} row={item} bind:row_size/>
              </VirtualList>
              <p>showing image rows {start+1}-{end}. Total Rows: {prepared_display.length} - Total Images: {prepared_display.reduce((count, current) => count + current.length, 0)}</p>
            {/if}
          </div>
    </div>
  </div>
</main>

<style>

#target_text{
  margin-top: 0.2em;
  color: red;
  font-weight: bold;
}

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
  width: 80%;
  float: left;
  margin-left: 2em;
}

.centering{
  display: flex;
  flex-direction: row;
  justify-content: center;
  width: 100%;
}

.horizontal{
  display: flex;
  flex: 1;
}
.resize-text{
  font-size: 0.75em;
}

.file-drop-area {
  position: relative;
  display: flex;
  align-items: center;
  height: 2em;
  margin-left: 1em;
  margin-right: 1em;
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
  margin-top: -0.6em;
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

#text_query_input{
  height: 10em;
  margin-top: 2em;
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
