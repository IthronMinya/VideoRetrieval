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
	
	// grab some place holder images
  async function fetchData() {
    const res = await fetch("https://jsonplaceholder.typicode.com/photos?_start=0&_limit=100");
    const data = await res.json();

    if (res.ok) {
      return data;
    } else {
      throw new Error(data);
    }
  }

  let prev_scores = [];
  
  let scores = [];

  let rand = -1;

  let lion_text_query = "";

  // demonstration of python backend call syntax
  function getRand() {
    fetch("./rand")
      .then(d => d.text())
      .then(d => (rand = Number(d)));

  }

  async function get_scores_by_text() {
    await fetch("./search_clip_text?text="+lion_text_query)
      .then(d => d.text())
      .then(d => console.log(d));

  }

  let clicked = 0;

</script>

<main>
  <div class='viewbox'>
    <div class='menu'>
      <h4 class="menu_item">Rerank images based on different metrics</h4>
      <div class='buttons'>
        <input bind:value={lion_text_query} />
        <Button class="menu_item menu_button" color="secondary" on:click={get_scores_by_text} variant="raised">
          <Label>CLIP Text Query</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>CLIP Similar Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Bayes Update</Label>
        </Button><br><br>
        <Button class="menu_item menu_button" color="primary" on:click={() => clicked++} variant="raised">
          <Label>Sent Selected Images</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Reset Last Action</Label>
        </Button>
        <Button class="menu_item menu_button" color="secondary" on:click={() => clicked++} variant="raised">
          <Label>Reset All Actions</Label>
        </Button>
      </div>
    </div>
    
    <div class="separator">
      <p> </p>
    </div>
    <!-- PLACE IMAGES WITHIN SUCH CARDS USING BACKEND! For now dummy content ahead -->
    <div id='image_container'>
      <LayoutGrid>
        {#await fetchData()}
            <p>loading</p>
        {:then items}
          {#each items as image}
            <Cell>
              <div class="card-display">
                <div class="card-container">
                  <Card>
                    <PrimaryAction on:click={() => clicked++}>
                      <img use:lazyLoad={image.url} alt={image.title} />
                      <Content class="mdc-typography--body2">
                        And some info text. And the media and info text are a primary action
                        for the card.
                      </Content>
                    </PrimaryAction>
                  </Card>
                </div>
              </div>
            </Cell>
          {/each}
        {:catch error}
          <p style="color: red">{error.message}</p>
        {/await}
      </LayoutGrid>
    </div>
  </div>
</main>

<style>
.card-display {
  display: flex;
  flex-wrap: wrap;
  justify-content: stretch;
}

.card-container {
  display: inline-flex;
  /* justify-content: center; */
  align-items: center;
  min-height: 200px;
  max-width: 100%;
  overflow-x: auto;
  background-color: var(--mdc-theme-background, #f8f8f8);
  border: 1px solid
    var(--mdc-theme-text-hint-on-background, rgba(0, 0, 0, 0.1));

  padding: 20px;

  margin-right: 20px;
  margin-bottom: 20px;
}

.card-container {
  margin: 0 auto;
}

</style>
