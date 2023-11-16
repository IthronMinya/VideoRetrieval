<script>
    import Image from './Image.svelte';
    import { createEventDispatcher } from 'svelte';
    export let row;
    export let row_size;
    const dispatch = createEventDispatcher()

    function similarimage(image_id){

        dispatch('similarimage', {image_id});
    }

</script>

<style>
	.row {
        display: table;
        border-collapse: collapse;
        width: 100%;
    }
    .item {
        display: table-cell;
        vertical-align: top;
        padding: 5px;
        position: relative;
        width: calc( 100% / var(--row_size));
    }

    
</style>

<div class="row">
	{#each row as img, index}
        <div class="item" style='--row_size:{row_size};'>
            <Image on:similarimage={() => similarimage(img.id)} {img}/>
        </div>
	{/each}
</div>

    
