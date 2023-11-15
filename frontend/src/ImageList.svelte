<script>
    import Image from './Image.svelte';
    import { createEventDispatcher } from 'svelte'
    export let row;
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
        width: 20%;
    }

    
</style>

<div class="row">
	{#each row as img, index}
        <div class="item">
            <Image on:similarimage={() => similarimage(img.id)} {img}/>
        </div>
	{/each}
</div>

    
