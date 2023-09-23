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
	
  var image_border_states = {};

  var num_image = 1000;

	// grab some place holder images
  async function fetchData(image_ids) {
    const res = await fetch("https://jsonplaceholder.typicode.com/photos?_start=0&_limit="+num_image);
    const data = await res.json();

    if (res.ok) {
      return data;
    } else {
      throw new Error(data);
    }
  }

  let prev_scores = [];
  
  let scores = [];

  let lion_text_query = "";

  let selected_images = [];

  let num_top_display = 200;

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_text() {
    await fetch("./search_clip_text?text="+lion_text_query)
      .then(d => d.text())
      .then(d => console.log(d));
  }

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_image() {

    if (selected_images.length == 0){
      // TODO make a popup alert and do nothing
      return null;
    }

    await fetch("./search_clip_image?image_id="+selected_images.slice(-1))
      .then(d => d.text())
      .then(d => console.log(d));
  }

  // TODO after confirming functionality write data to scores, determine images ids to display from scores in descending score order, place into image_ids, use load_display() to render
  async function get_scores_by_bayes_update() {

  if (selected_images.length == 0){
    // TODO make a popup alert and do nothing
    return null;
  }

  var keys = []

  for(var key of Object.keys(image_border_states).slice(0, num_top_display))
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
    .then(d => console.log(d));
  }

  let clicked = 0;

  let display = {};

  function load_display() {
    fill_state_dict();
    display = {};
  }

  function fill_state_dict(){

    for(var id of image_ids){
      image_border_states[id] = false;
    }
  }

  let image_ids = [];

  // TODO update this init for production
  for(let i = 1; i <= num_image; i++){
    image_ids.push(i);
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
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_image} variant="raised">
          <Label>Similar Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_bayes_update} variant="raised">
          <Label>Bayes Update</Label>
        </Button><br><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Send Selected Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Reset Last Action</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Reset All Actions</Label>
        </Button>
        <!-- <button on:click={load_display}>Restart</button> -->
      </div>
    </div>
    
    <div class="separator">
      <p> </p>
    </div>
    <!-- dummy content ahead -->
    {#key display}
    <div id='image_container'>
      <LayoutGrid>
        {#await fetchData(image_ids)}
            <p>loading</p>
        {:then items}
          {#each items as image}
            <PrimaryAction id={image.id} class="{image_border_states[image.id] ? 'redBorder' : ''}" on:click={() => imageClick(image.id)} >
              <img use:lazyLoad={image.url} alt={image.id} />
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

</style>
