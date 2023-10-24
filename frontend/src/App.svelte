<script>
  import Button, { Label } from '@smui/button';
  
  import LayoutGrid, { Cell } from '@smui/layout-grid';

  // @ts-ignore
  import Select, { Option } from '@smui/select';
  import {PrimaryAction} from '@smui/card';

  import { lazyLoad } from './lib/lazyload.js'
  import Dropzone from "svelte-file-dropzone/Dropzone.svelte";
  
  let random_target = null;
  
  let files = {
    accepted: [],
    rejected: []
  };

  function handleFilesSelect(e) {
    const { acceptedFiles, fileRejections } = e.detail;
    files.accepted = [...files.accepted, ...acceptedFiles];
    files.rejected = [...files.rejected, ...fileRejections];

    console.log(files.accepted);
    document.getElementById("filedrop-box").style.width = "50%";
    document.getElementById("filedrop-box").style.float = "left";
    document.getElementById("filedrop-box").style.marginBottom = "7.5px";
  }

  var image_border_states = {};

  var image_hover_states = {image_hover_states};

  var num_image = 1000;

  // @ts-ignore
  let test_image = null;

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
	// grab some place holder images
  async function fetchData(image_items) {
    //let sorted_keys = getKeysInDescendingOrder(image_items);
    //console.log(sorted_keys);

    let res = await fetch("https://jsonplaceholder.typicode.com/photos?_start=0&_limit="+num_image);
    let data = await res.json();

    // @ts-ignore
    let chart_data = {
      labels: ['Person', 'Car', 'Maple Tree', 'Dog', 'Cat'],
      datasets: [
        {
          data: [2000, 1000, 150, 500, 350],
          backgroundColor: [
            '#F7464A',
            '#46BFBD',
            '#FDB45C',
            '#949FB1',
            '#4D5360',
            '#AC64AD',
          ],
          hoverBackgroundColor: [
            '#FF5A5E',
            '#5AD3D1',
            '#FFC870',
            '#A8B3C5',
            '#616774',
            '#DA92DB',
          ],
        },
      ],
    };

    create_chart(chart_data);
    
    if (res.ok) {
      console.log(image_items);
      return image_items;
    } else {
      throw new Error(data);
    }
    
  }

  function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

  let lion_text_query = "text query";

  let custom_result = "custom text";

  let selected_images = [];

  let max_display_size = 4000;

  let display_size = max_display_size;

  let test_image_av = false;

  async function initialization() {
    const request_body = {
      item_id: "00001_1",
      k: 50
    };

    try {
      const response = await fetch("http://acheron.ms.mff.cuni.cz:42032/getVideoFrames/", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request_body)
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      const responseData = await response.json();
      console.log(responseData);
      image_items = responseData;

    } catch (error) {
      console.error(error);
    }
  }

  async function get_scores_by_text() {
    const request_body = {
      query: lion_text_query,
      k: 50,
      dataset: 'vbs',
      model: 'laion',
      get_embeddings: true,
    };

    try {
      const response = await fetch("http://acheron.ms.mff.cuni.cz:42032/textQuery/", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request_body)
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      const responseData = await response.json();
      console.log(responseData);
      image_items = responseData;
      load_display();

    } catch (error) {
      console.error(error);
    }

  }

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_image() {

    if (selected_images.length == 0){
      // TODO make a popup alert and do nothing
      return null;
    }

    await fetch("./search_clip_image?image_id="+selected_images.slice(-1))
      .then(d => d.text())
      .then(d => console.log(d))
      .then(d => previous_image_items.push(image_items))
      .then(d => load_display());
  }

   // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
   async function get_scores_by_image_upload() {

      if (files.accepted.length == 0){
        // TODO make a popup alert and do nothing
        return null;
      }
      
      // TODO send file files.accepted[-1] to backend for reranking
      await fetch("./search_clip_image?image_id="+selected_images.slice(-1))
        .then(d => d.text())
        .then(d => console.log(d))
        .then(d => previous_image_items.push(image_items))
        .then(d => load_display());
        
    }

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_bayes_update() {

    if (selected_images.length == 0){
      // TODO make a popup alert and do nothing
      return null;
    }

    var keys = []

    for(var key of Object.keys(image_border_states).slice(0, display_size))
    {
      keys.push(parseInt(key));
    }

    console.log("./bayes_update?selected_ids=["+selected_images+"]&top_display=["+keys+"]")

    await fetch('./bayes_update',{
        method:  'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          selected_ids: selected_images,
          top_display:  keys
        })
      })
      .then(d => d.text())
      .then(d => console.log(d))
      // @ts-ignore
      // @ts-ignore
      .then(d => previous_image_items.push(image_items))
      // @ts-ignore
      // @ts-ignore
      .then(d => load_display());
  }

  let clicked = 0;

  let display = {};

  function load_display() {
    fill_state_dict();
    display = {};
  }

  function getKeysInDescendingOrder(obj) {
    // Create an array of key-value pairs
    const keyValuePairs = Object.entries(obj);

    // Sort the array based on values in descending order
    keyValuePairs.sort((a, b) => b[1] - a[1]);

    // Extract the keys in the sorted order
    const sortedKeys = keyValuePairs.map(pair => pair[0]);

    return sortedKeys;
  }

  function fill_state_dict(){

    for(var id of Object.keys(image_items)){
      image_border_states[id] = false;
      image_hover_states[id] = false;
    }
  }

  let previous_image_items = [];

  let image_items = {};

  image_items = initialization();
  // random initialization
  //for(let i = 1; i <= max_display_size; i++){
  //  image_items[getRandomInt(max_display_size)] = Math.random();
  //}

  fill_state_dict();

  function imageClick(image_id) {
    image_border_states[image_id] = !image_border_states[image_id];

    if (image_border_states[image_id]){
      selected_images.push(image_id);
    }else{
      selected_images = selected_images.filter(e => e !== image_id);
    }
    
    console.log(image_id);

    console.log(selected_images);
  }

  function reset_last(){
    if (previous_image_items.length > 0){
      image_items = previous_image_items.pop()
    }

    load_display()
  }

  function reset_all(){
    previous_image_items = []

    // random initialization
    for(let i = 1; i <= max_display_size; i++){
      image_items[getRandomInt(max_display_size)] = Math.random();
    }

    load_display()
  }

  // @ts-ignore
  function create_chart(data){

    //var ctx = document.getElementById('myChart');
    // @ts-ignore
    var ctx = document.getElementById('myChart').getContext('2d'); // 2d context
    //var ctx = 'myChart'; // element id

    // @ts-ignore
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: ['Person', 'Car', 'Maple Tree', 'Dog', 'Cat'],
        datasets: [{
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

  let datasets = ['VBS', 'Medical'];
 
  let value = 'VBS';

  let username = "username";

</script>

<main>
  <div class='viewbox'>
    <div class='menu'>
      <br>
      <!-- <h3 class="menu_item">Re-Rank Images</h3> -->
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
        <input class="menu_item" bind:value={lion_text_query} />
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_text} variant="raised">
          <Label>Submit Text Query</Label>
        </Button>
        <div class="filedrop-container menu_item">
          <div id="filedrop-box">
            
            <Dropzone on:drop={handleFilesSelect} accept={["image/*"]} containerClasses="custom-dropzone">
              <span>Click / Drag and drop</span>
            </Dropzone>
          </div>
          {#if files.accepted.length > 0}
            <div id="image-preview-container">
              <img id="output" alt="preview upload" src={URL.createObjectURL(files.accepted[files.accepted.length - 1])}/>
            </div>
          {/if}
        </div>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image_upload} variant="raised">
          <Label>Similar Images by Upload</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image} variant="raised">
          <Label>Similar Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_bayes_update} variant="raised">
          <Label>Bayes Update</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={reset_last} variant="raised">
          <Label>Reset Last Action</Label>
        </Button>
        <!-- <Button class="menu_item menu_button" color="secondary" on:click={reset_all} variant="raised">
          <Label>Reset All Actions</Label>
        </Button>-->
        
        <canvas class="menu_item" id="myChart" style="width:300px;height:300px;"></canvas>

        <Button class="menu_item menu_button" color="secondary" on:click={reset_all} variant="raised">
          <Label>Must Contain Selected Classes</Label>
        </Button><br><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send Selected Images</Label>
        </Button>
        <input class="menu_item" bind:value={custom_result} /><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send custom text</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={reset_all} variant="raised">
          <Label>Download Test Data</Label>
        </Button><br><br>
        <input class="menu_item" bind:value={username} />
        <div class="menu_item">
          <div id="select-dataset">
            <Select bind:value label="Select Dataset">
              {#each datasets as dataset}
                <Option value={dataset}>{dataset}</Option>
              {/each}
            </Select>
          </div>
        </div>
        <!-- <button on:click={load_display}>Restart</button> -->
      </div>
    </div>
    
    <div class="separator">
      <p> </p>
    </div>
    {#key display}
    <div id='image_container'>
      <LayoutGrid>
        {#await fetchData(image_items)}
            <p>loading</p>
        {:then items}
          {#each items as image}
            <PrimaryAction id={image.id} class="{image_border_states[image.id] ? 'redBorder' : ''}" on:click={() => imageClick(image.id) }  on:mouseover={() => (image_hover_states[image.id] = true)} on:mouseout={() => (image_hover_states[image.id] = false)} >
              <img class="images" use:lazyLoad={"http://acheron.ms.mff.cuni.cz:42032/images/" + image['uri']} alt={image['id']}/>
              {#if image_hover_states[image.id]}
                <button class="hoverbutton">Send</button>
              {/if}
            </PrimaryAction>
          {/each}
        {:catch error}
          <p style="color: red">{error.message}</p>
        {/await}
      </LayoutGrid>
    </div>
    {/key}
  </div>
</main>

<style>

.hoverbutton{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 10px 20px;
  border: none;
  cursor: pointer;
}

.filedrop-container{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 90%;
}

#image-preview-container{
  width: 50%;
  height: 6em;
  float: left;
}

#output{
  height: 100%;
  width: 100%;
  object-fit: contain;
}

#testimage{
  height: 100%;
  width: 100%;
  object-fit: contain;
}

.images{
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
