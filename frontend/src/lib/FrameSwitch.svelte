<script lang="ts">
	import ChipGroup from './ChipGroup.svelte';
	import { FRAMES, type FrameId } from './projection';

	interface Props {
		frame: FrameId;
	}
	let { frame = $bindable() }: Props = $props();

	const LABELS: Record<FrameId, string> = {
		greece: 'Greece',
		'aegean-east': 'Eastern Aegean',
		epirus: 'Epirus',
		cyprus: 'Cyprus'
	};
	const items = (Object.keys(LABELS) as FrameId[])
		.filter((f) => f in FRAMES)
		.map((f) => ({ id: f, label: LABELS[f] }));
</script>

<!-- One frame at a time, so a pick replaces rather than toggles. -->
<ChipGroup
	label="Frame"
	{items}
	selected={[frame]}
	ontoggle={(id) => (frame = id as FrameId)}
/>
