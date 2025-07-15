import { writable } from 'svelte/store';

export let selected_images = writable([]);
export let scroll_height = writable(0);
export let in_video_view = writable(false);
export let lion_text_query = writable('');
export let lion_text_query_scene_2 = writable('');
export let is_login = writable(false);
export let username = writable('prak_test');
export let password = writable('');
