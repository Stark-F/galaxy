<template>
    <div class="navigation">
        <b-dropdown v-if="breadCrumbOptions.length" class="mr-auto" size="sm" text="Go to..." boundary="viewport">
            <b-dropdown-item @click="close"> History: {{ history.name }} </b-dropdown-item>
            <b-dropdown-item v-for="option in breadCrumbOptions" :key="option.key" @click="reselect(option.value)">
                {{ option.text }}
            </b-dropdown-item>
        </b-dropdown>

        <b-button v-else size="sm" class="mr-auto back" @click="close"> Back to: {{ history.name }} </b-button>

        <PriorityMenu :starting-height="27">
            <PriorityMenuItem
                key="download-collection"
                title="Download Collection"
                icon="fas fa-file-download"
                tag="a"
                download
                :href="downloadCollectionUrl"
            />
            <PriorityMenuItem key="back-up" title="Back One" icon="fas fa-level-up-alt" @click="back" />
        </PriorityMenu>
    </div>
</template>

<script>
import { History } from "../model";
import { PriorityMenuItem, PriorityMenu } from "components/PriorityMenu";

export default {
    components: {
        PriorityMenuItem,
        PriorityMenu,
    },
    props: {
        history: { type: History, required: true },
        selectedCollections: { type: Array, required: true, validate: (val) => val.length > 0 },
    },
    computed: {
        rootCollection() {
            return this.selectedCollections[0];
        },

        // List for the dropdown. Should be the history and every parent
        // collection excepting the current one.
        breadCrumbOptions() {
            const parents = this.selectedCollections.slice(0, -1);
            const options = parents.map((bc, i) => {
                return {
                    key: bc.type_id,
                    value: parents.slice(0, i + 1),
                    text: bc.name,
                };
            });
            return options;
        },

        downloadCollectionUrl() {
            let url = "";
            if (this.rootCollection) {
                url = `${this.rootCollection.url}/download`;
            }
            return url;
        },
    },
    methods: {
        reselect(newList) {
            this.$emit("update:selectedCollections", newList);
        },
        back() {
            const newList = this.selectedCollections.slice(0, -1);
            this.reselect(newList);
        },
        close() {
            this.reselect([]);
        },
    },
};
</script>
