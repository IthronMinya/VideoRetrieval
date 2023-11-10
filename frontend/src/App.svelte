<script>
// @ts-nocheck

  import { selected_images } from './stores.js';
  import ImageList from './ImageList.svelte';

  import VirtualList from '@sveltejs/svelte-virtual-list';
  
  import Button, { Label } from '@smui/button';

  // @ts-ignore
  import Select, { Option } from '@smui/select';


  let lion_text_query = "";

  let start;
	let end;
  let image_items = {}
  let alpha = 0.1;

  let custom_result = "";

  let max_display_size = 4000;

  let test_image_av = false;

  const row_size = 5;

  $: image_items;

  let random_target = null;
  
  let files = {
    accepted: [],
    rejected: []
  };

  let clicked = 0;

  let previous_image_items = [];

  let datasets = ['V3C', 'Medical'];

  let models = ['clip-laion', 'clip-openai'];
 
  let value_dataset = 'V3C';

  let value_model = 'clip-laion';

  let username = "";

  let action_log = [];

  let bayes_display = 10 * row_size;

  let dragged_url = null;

  image_items = initialization();


  function noopHandler(evt) {
      evt.preventDefault();
  }
  
  function drop(evt) {

    evt.preventDefault();
    const file = evt.dataTransfer.files[0];

    console.log(evt.dataTransfer.files);

    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();

      reader.onload = () => {
        dragged_url = reader.result;
      };

      reader.readAsDataURL(file);
    }
  }

  async function get_test_image(){
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
    
    const request_url = "http://acheron.ms.mff.cuni.cz:42032/getVideoFrames/";

    const request_body = JSON.stringify({
      item_id: "00001_1",
      k: 50
    });

    await request_handler(request_url, request_body, true);
    
  }

  function handleKeypress(event){
    var key=event.keyCode || event.which;
    if (key==13){
      get_scores_by_text();
    }
  }

  async function request_handler(request_url, request_body, init=false, image_upload=false){

    if(!init){
      previous_image_items.push(image_items);

      image_items = null;
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

      let rows = [];
      let row = -1;

      for (let i = 0; i < responseData.length; i++) {
        if (i % row_size == 0){
          row = row + 1;
          rows[row] = [];
        }

        rows[row].push(responseData[i]);

      }

      image_items = rows;

      if(!init){
        $selected_images = [];
      }
      
      create_chart(image_items);

    } catch (error) {
      console.error(error);
    }

  }

  async function get_scores_by_text() {

    action_log.push({'method': 'textquery', 'query': lion_text_query, 'k': max_display_size});

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/textQuery/";

    const request_body = JSON.stringify({
      query: lion_text_query,
      k: max_display_size,
      dataset: 'vbs',
      model: 'clip-laion',
      get_embeddings: true,
    });

    await request_handler(request_url, request_body);
  }

  async function get_scores_by_image() {


    if ($selected_images.length == 0){
      return null;
    }

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQueryByID/";

    let selected_item = $selected_images[$selected_images.length - 1]

    action_log.push({'method': 'image_internal_query', 'query': [selected_item[0], selected_item[1]], 'k': max_display_size});

    const request_body = JSON.stringify({
      video_id: selected_item[0],
      frame_id: selected_item[1],
      k: max_display_size,
      dataset: 'vbs',
      model: 'clip-laion',
      add_features : true,
    });


    await request_handler(request_url, request_body);
  }
  
  async function get_scores_by_image_upload() {


    if (files.accepted.length == 0){
      return null;
    }

    const request_url = "http://acheron.ms.mff.cuni.cz:42032/imageQuery/";
    
    action_log.push({'method': 'image_upload_query', 'query': 'uploaded image', 'k': max_display_size});

    const params = {
      k: max_display_size,
      dataset: 'vbs',
      model: 'clip-laion',
      add_features : true,
    };

    const request_body = new FormData();
    request_body.append('image', files.accepted[files.accepted.length - 1]);
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

    previous_image_items.push(image_items);

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

    action_log.push({'method': 'bayes', 'query': $selected_images, 'k': topDisplay});

    // @ts-ignore
    const negativeExamplesIndices = items.filter(item => !topDisplay.includes(item) && !selected_images.includes(item));
    const positiveExamplesIndices = items.filter(item => selected_images.includes(item));

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

  function reset_last(){
    if (previous_image_items.length > 0){
      image_items = previous_image_items.pop()
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
    <div class='menu'>
      <br>
      <div class='buttons'>
        <Button class="menu_item menu_button" color="secondary" on:click={get_test_image} variant="raised">
          <Label>Random Test Image</Label>
        </Button>
        {#if true}
          <div id="test-image-preview-container">
            <img id="testimage" alt="" />
          </div>
        {/if}
        <br><br>
        <input class="menu_item" bind:value={lion_text_query} placeholder="Your text query" on:keypress={handleKeypress}/>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_text} variant="raised">
          <Label>Submit Text Query</Label>
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
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image_upload} variant="raised">
          <Label>Similar Images by Upload</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image} variant="raised">
          <Label>Similar Images to Last Selection</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={bayesUpdate} variant="raised">
          <Label>Bayes Update</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={reset_last} variant="raised">
          <Label>Reset Last Action</Label>
        </Button>
        <canvas class="menu_item" id="myChart" style="width:300px;height:300px;"></canvas>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Must Contain Selected Classes</Label>
        </Button><br><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send Selected Images</Label>
        </Button>
        <input class="menu_item" bind:value={custom_result} placeholder="Your custom result message"/><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send custom text</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Download Test Data</Label>
        </Button><br><br>
        <input class="menu_item" bind:value={username} placeholder="Your username"/>
        <div class="menu_item">
          <div id="select-dataset">
            <Select bind:value_dataset label="Select Dataset">
              {#each datasets as dataset}
                <Option value={dataset}>{dataset}</Option>
              {/each}
            </Select>
          </div>
        </div>
        <div class="menu_item">
          <div id="select-model">
            <Select bind:value_model label="Select Model">
              {#each models as model}
                <Option value={model}>{model}</Option>
              {/each}
            </Select>
          </div>
        </div>
      </div>
    </div>
    <div class="separator">
      <p> </p>
    </div>
    {#key image_items}
      <div id='container'>
        {#if image_items === null}
          <p>...loading</p>
        {:else}
          {#await image_items}
            <p>...loading</p>
          {:then imageData}
            <VirtualList items={imageData} bind:start bind:end let:item>
              <ImageList row={item} />
            </VirtualList>
            <p>showing image rows {start}-{end}. Total: {image_items.length}</p>
          {/await}
        {/if}
      </div> 
    {/key}
</main>

<style>

.file-drop-area {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0.5em;
  border: 1px dashed rgba(61, 61, 61, 0.4);
  border-radius: 3px;
  transition: 0.2s;
  &.is-active {
    background-color: rgba(255, 255, 255, 0.05);
  }
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
  height: calc(100vh - 5em);
  width: 85%;
  float: left;
  margin-left: 15%;
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

#select-dataset{
  width: 100%;
  height: 100%;
  object-fit: contain;
}

</style>
