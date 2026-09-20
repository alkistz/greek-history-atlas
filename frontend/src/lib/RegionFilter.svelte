<script lang="ts">
	import ChipGroup from './ChipGroup.svelte';
	import { t } from './lang.svelte';
	import type { Region } from './types';

	interface Props {
		regions: Region[];
		/** selected region ids; empty means the whole map */
		selected: string[];
		ontoggle: (id: string) => void;
		onclear: () => void;
	}
	let { regions, selected, ontoggle, onclear }: Props = $props();

	const items = $derived(regions.map((r) => ({ id: r.id, label: t(r.name) })));
</script>

<!-- Every region is listed rather than hidden behind a menu: Cyprus and Asia Minor
     are not visible in the default frame, so the map alone could never reach them. -->
<div class="wrap">
	<ChipGroup label="Region" quiet {items} {selected} {ontoggle} {onclear} />
</div>

<style>
	.wrap {
		margin-bottom: 10px;
	}
</style>
