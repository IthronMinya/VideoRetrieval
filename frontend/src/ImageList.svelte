<script>
    import Image from './Image.svelte';
    import { createEventDispatcher } from 'svelte';
    export let row;
    export let row_size;
    const dispatch = createEventDispatcher()

    function similarimage(image_id){

        dispatch('similarimage', {image_id});
    }

    function send_result(image_id){
        dispatch('send_result', {image_id});
    }

</script>

<style>
	.row {
        display: flex;
        flex-wrap: wrap;
    }

    .item {
        box-sizing: border-box;
        flex: 1 0 auto; /* Allow items to grow, but not shrink */
        position: relative; /* Make the container relative */
        width: calc(100% / var(--row_size) ); /* Account for padding and margin */
    }

    
</style>

<div class="row">
	{#each row as img, index}
        <div class="item" style='--row_size:{row_size};'>
            <Image on:send_result={() => send_result(img.id)} on:similarimage={() => similarimage(img.id)} {img} row_size={row.length}/>
        </div>
	{/each}
</div>

    
