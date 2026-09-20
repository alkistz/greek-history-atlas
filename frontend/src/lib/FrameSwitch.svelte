<script lang="ts">
	import ChipGroup from './ChipGroup.svelte';
	import { FRAMES, type FrameId } from './projection';
	import { term, ui } from './ui';

	interface Props {
		frame: FrameId;
	}
	let { frame = $bindable() }: Props = $props();

	// The order is the one the chips read in, and is not the order `FRAMES` happens
	// to be written in.
	const ORDER: FrameId[] = ['greece', 'aegean-east', 'epirus', 'cyprus'];
	const items = $derived(
		ORDER.filter((f) => f in FRAMES).map((f) => ({ id: f, label: term('frame', f) }))
	);
</script>

<!-- One frame at a time, so a pick replaces rather than toggles. -->
<ChipGroup
	label={ui('facet.frame')}
	{items}
	selected={[frame]}
	ontoggle={(id) => (frame = id as FrameId)}
/>
