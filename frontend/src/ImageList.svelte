<script>
    import Image from './Image.svelte';
    import { selected_images } from './stores.js';
    import { createEventDispatcher } from 'svelte';
    export let row;
    export let row_size;
    let images = [];

    const dispatch = createEventDispatcher()

    function similarimage(image_id){

        dispatch('similarimage', {image_id});
    }

    function video_images(image_id){

        dispatch('video_images', {image_id});
    }

    function send_result(image_id){
        dispatch('send_result', {image_id});
    }

</script>

<style>
	.row {
        display: flex;
        flex-wrap: nowrap;
        box-sizing: border-box;
        width: calc((100% / var(--row_size)) * var(--row_items) )
    }

    .item {
        box-sizing: border-box; /* Account for padding and margin */
        flex: 1 0 auto; /* Allow items to grow, but not shrink */
        position: relative;
        width: calc(100% / var(--row_size) );
    }

    
</style>

<div class="row" style='--row_size:{row_size};--row_items:{row.length};'>
	{#each row as img, index}
        <div class="item">
            <Image bind:this={images[index]} on:send_result={() => send_result(img.id)} on:similarimage={() => similarimage(img.id)} on:video_images={() => video_images(img.id)} {img} row_size={row.length} selected={$selected_images.includes(img.id)}/>
        </div>
	{/each}
</div>

    
