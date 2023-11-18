<script>
// @ts-nocheck

  import { selected_images } from './stores.js';
  import ImageList from './ImageList.svelte';

  import Timer from './Timer.svelte';

  import VirtualList from '@sveltejs/svelte-virtual-list';
  
  import Button from '@smui/button';

  // @ts-ignore
  import Select, { Option } from '@smui/select';
  
  import Fab, { Label, Icon } from '@smui/fab';

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

  initialization();

  function handleResize(){
    row_size = Math.floor(window.innerWidth / 350);

    if (image_items[action_pointer] != null){
      console.log("resizing...");
      let rows = [];
      let row = -1;

      for (let i = 0; i < image_items[action_pointer].length; i++) {
        if (i % row_size == 0){
          row = row + 1;
          rows[row] = [];
        }

        rows[row].push(image_items[action_pointer][i]);

      }

      start = 0;

      prepared_display = rows;
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
  }

  function send_results_single(event){
    timer.stop();

    send_results = event.detail.image_id;

    $selected_images = [];

  }

  function send_results_multiple(){
    timer.stop();

    send_results = " ";

    $selected_images.forEach((selection) => {
      send_results += `${selection}; `;
    });

    send_results = send_results.slice(0, -2); // remove last space and semicolon

    $selected_images = [];
  }

  function download_results(){
    
  }

  async function get_test_image(){

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

  async function initialization() {
    
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
            k: 100/2,
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

      console.log(action_log_without_back_and_forth);

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

      const responseData = await response.json();

      console.log(responseData);

      image_items[action_pointer] = responseData;

      handleResize();
      
      if(!init){
        $selected_images = [];
      }

      create_chart(image_items[action_pointer]);

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
    }

    if (action_log_without_back_and_forth[action_log_pointer-1]['method'] == "textquery"){
      lion_text_query = action_log_without_back_and_forth[action_log_pointer-1]['query'];
    }
    
    if (image_items.length - 1 > action_pointer){
      
      if(image_items[action_pointer + 1] === null){
        image_items.pop();
      }else{
        action_pointer += 1;
        image_items = image_items;
      }

      action_log.push({'method': 'forward'});

    }
  }

  function reset_last(){
    
    if(action_log_pointer > 1){
      action_log_pointer -=1;
    }

    if (action_log_without_back_and_forth[action_log_pointer -1]['method'] == "textquery" ||
       action_log_without_back_and_forth[action_log_pointer -1]['method'] == "initialization"){
        lion_text_query = action_log_without_back_and_forth[action_log_pointer-1]['query'];
    }

    if (image_items.length > 0 && action_pointer > 0){
      action_pointer -= 1;
            
      image_items = image_items;

      action_log.push({'method': 'back'});
    }
  }

  // @ts-ignore
  function create_chart(image_items){

    //var ctx = document.getElementById('myChart');
    // @ts-ignore
    var ctx = document.getElementById('myChart').getContext('2d'); // 2d context
    //var ctx = 'myChart'; // element id

    // @ts-ignore
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ['Person', 'Car', 'Maple Tree', 'Dog', 'Cat'],
        datasets: [{
          label: 'Display Clusters',
          backgroundColor: [
            '#F7464A',
            '#46BFBD',
            '#FDB45C',
            '#949FB1',
            '#4D5360',
            '#AC64AD',
          ],
          data: [2000, 1000, 150, 500, 350]
        }]
      }
    });
    

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
          <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
            <span class="resize-text">Must Contain Selected Classes</span>
          </Button>
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
                  <ImageList on:send_result={send_results_single} on:similarimage={get_scores_by_image} row={item} bind:row_size/>
                </VirtualList>
                <p>showing image rows {start}-{end}. Total: {prepared_display.length}</p>
              {/await}
            {/if}
          </div>
        {/key}
      {/key}
    </div>
  </div>
</main>

<style>


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
