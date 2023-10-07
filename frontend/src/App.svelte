<script>
  import Button, { Label } from '@smui/button';
  import LayoutGrid, { Cell } from '@smui/layout-grid';
  import Card, {
      Content,
      PrimaryAction,
      Media,
      MediaContent,
    } from '@smui/card';

  import { lazyLoad } from './lib/lazyload.js'
  import Dropzone from "svelte-file-dropzone/Dropzone.svelte";

  let files = {
    accepted: [],
    rejected: []
  };

  function handleFilesSelect(e) {
    const { acceptedFiles, fileRejections } = e.detail;
    files.accepted = [...files.accepted, ...acceptedFiles];
    files.rejected = [...files.rejected, ...fileRejections];

    console.log(files.accepted);	  
  }

  var image_border_states = {};

  var image_hover_states = {image_hover_states};

  var num_image = 1000;

	// grab some place holder images
  async function fetchData(image_items) {
    let sorted_keys = getKeysInDescendingOrder(image_items);
    console.log(sorted_keys);

    const res = await fetch("https://jsonplaceholder.typicode.com/photos?_start=0&_limit="+num_image);
    const data = await res.json();

    if (res.ok) {
      return data;
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

  let max_display_size = 4000

  let display_size = max_display_size;

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_text() {
    await fetch("./search_clip_text?text="+lion_text_query)
      .then(d => d.text())
      .then(d => console.log(d))
      .then(d => previous_image_items.push(image_items))
      .then(d => load_display());
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
      .then(d => previous_image_items.push(image_items))
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

  // random initialization
  for(let i = 1; i <= max_display_size; i++){
    image_items[getRandomInt(max_display_size)] = Math.random();
  }

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

</script>

<main>
  <div class='viewbox'>
    <div class='menu'>
      <h3 class="menu_item">Re-Rank Images</h3>
      <div class='buttons'>
        <input class="menu_item menu_button" bind:value={lion_text_query} /><br>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_text} variant="raised">
          <Label>Submit Text Query</Label>
        </Button>
        <div class="filedrop-container">
          <div class="filedrop">
            <Dropzone on:drop={handleFilesSelect} accept={["image/*"]} containerClasses="custom-dropzone">
              <button>Choose images to upload</button>
              <span>or</span>
              <span>Drag and drop them here</span>
            </Dropzone>
            {#if files.accepted.length > 0}
              <!--<span>{files.accepted[files.accepted.length - 1].name}</span>-->
              <br>
              <img id="output" width="50" height="50" alt="preview upload" src={URL.createObjectURL(files.accepted[files.accepted.length - 1])}/>
            {/if}
          </div>
        </div><br>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image_upload} variant="raised">
          <Label>Similar Images by Upload</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image} variant="raised">
          <Label>Similar Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_bayes_update} variant="raised">
          <Label>Bayes Update</Label>
        </Button>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send Selected Images</Label>
        </Button>
        <input class="menu_item menu_button" bind:value={custom_result} /><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send custom text</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={reset_last} variant="raised">
          <Label>Reset Last Action</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={reset_all} variant="raised">
          <Label>Reset All Actions</Label>
        </Button>
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
              <img class="images" use:lazyLoad={image.url} alt={image.id}/>
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
  width: 100%;
}

.filedrop{
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 90%;
}

</style>
