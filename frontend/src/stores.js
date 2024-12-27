import { writable } from 'svelte/store';

export let selected_images = writable([]);
export let scroll_height = writable(0);
export let in_video_view = writable(false);
export let lion_text_query = writable('');
export let is_login = writable(true);
export let username = writable('test');
export let password = writable('');
