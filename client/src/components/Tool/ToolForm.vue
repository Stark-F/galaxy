<template>
    <ConfigProvider v-slot="{ config }">
        <CurrentUser v-slot="{ user }">
            <UserHistories v-if="user" :user="user" v-slot="{ currentHistoryId }">
                <div v-if="currentHistoryId">
                    <LoadingSpan v-if="showLoading" message="Loading Tool" />
                    <div v-if="showEntryPoints">
                        <ToolEntryPoints v-for="job in entryPoints" :job-id="job.id" :key="job.id" />
                    </div>
                    <ToolSuccess
                        v-if="showSuccess"
                        :job-def="jobDef"
                        :job-response="jobResponse"
                        :tool-name="toolName"
                    />
                    <Webhook v-if="showSuccess" type="tool" :tool-id="jobDef.tool_id" />
                    <b-alert v-if="showError" show variant="danger">
                        <h4>{{ errorTitle | l }}</h4>
                        <p>
                            The server could not complete the request. Please contact the Galaxy Team if this error
                            persists.
                        </p>
                        <pre>{{ errorContentPretty }}</pre>
                    </b-alert>
                    <ToolRecommendation v-if="showRecommendation" :tool-id="formConfig.id" />
                    <ToolCard
                        v-if="showForm"
                        :id="formConfig.id"
                        :user="user"
                        :version="formConfig.version"
                        :title="formConfig.name"
                        :description="formConfig.description"
                        :options="formConfig"
                        :message-text="messageText"
                        :message-variant="messageVariant"
                        @onChangeVersion="onChangeVersion"
                        @onUpdateFavorites="onUpdateFavorites"
                        itemscope="itemscope"
                        itemtype="https://schema.org/CreativeWork"
                    >
                        <template v-slot:body>
                            <FormDisplay
                                :id="formConfig.id"
                                :inputs="inputs"
                                :validation-scroll-to="validationScrollTo"
                                :form-config="formConfig"
                                @onChange="onChange"
                                @onValidation="onValidation"
                            />
                            <FormElement
                                v-if="emailAllowed(config, user)"
                                id="send_email_notification"
                                title="Email notification"
                                help="Send an email notification when the job completes."
                                type="boolean"
                                v-model="useEmail"
                            />
                            <FormElement
                                v-if="remapAllowed"
                                id="rerun_remap_job_id"
                                :title="remapTitle"
                                :help="remapHelp"
                                type="boolean"
                                v-model="useJobRemapping"
                            />
                            <FormElement
                                v-if="reuseAllowed(user)"
                                id="use_cached_job"
                                title="Attempt to re-use jobs with identical parameters?"
                                help="This may skip executing jobs that you have already run."
                                type="boolean"
                                v-model="useCachedJobs"
                            />
                        </template>
                        <template v-slot:buttons>
                            <ButtonSpinner
                                id="execute"
                                title="Execute"
                                @onClick="onExecute(config, currentHistoryId)"
                                :wait="showExecuting"
                                :tooltip="tooltip"
                            />
                        </template>
                    </ToolCard>
                </div>
            </UserHistories>
        </CurrentUser>
    </ConfigProvider>
</template>

<script>
import { getGalaxyInstance } from "app";
import { getToolFormData, updateToolFormData, submitJob } from "./services";
import { allowCachedJobs } from "./utilities";
import ToolCard from "./ToolCard";
import ButtonSpinner from "components/Common/ButtonSpinner";
import CurrentUser from "components/providers/CurrentUser";
import ConfigProvider from "components/providers/ConfigProvider";
import LoadingSpan from "components/LoadingSpan";
import FormDisplay from "components/Form/FormDisplay";
import FormElement from "components/Form/FormElement";
import ToolSuccess from "./ToolSuccess";
import UserHistories from "components/History/providers/UserHistories";
import Webhook from "components/Common/Webhook";

export default {
    components: {
        ButtonSpinner,
        CurrentUser,
        ConfigProvider,
        LoadingSpan,
        FormDisplay,
        ToolCard,
        FormElement,
        ToolSuccess,
        UserHistories,
        Webhook,
    },
    props: {
        id: {
            type: String,
            default: null,
        },
        version: {
            type: String,
            default: null,
        },
        job_id: {
            type: String,
            default: null,
        },
        history_id: {
            type: String,
            default: null,
        },
    },
    data() {
        return {
            showLoading: true,
            showForm: false,
            showEntryPoints: false,
            showRecommendation: false,
            showSuccess: false,
            showError: false,
            showExecuting: false,
            error: null,
            formConfig: {},
            formData: {},
            remapAllowed: false,
            errorTitle: null,
            errorContent: null,
            messageVariant: "",
            messageText: "",
            useCachedJobs: false,
            useEmail: false,
            useJobRemapping: false,
            entryPoints: [],
            jobDef: {},
            jobResponse: {},
            validationInternal: null,
            validationScrollTo: null,
            validationErrors: null,
            currentVersion: this.version,
        };
    },
    created() {
        this.requestTool();
        const Galaxy = getGalaxyInstance();
        if (Galaxy && Galaxy.currHistoryPanel) {
            Galaxy.currHistoryPanel.collection.on("change", () => {
                this.onUpdate();
            });
        }
    },
    computed: {
        toolName() {
            return this.formConfig.name;
        },
        tooltip() {
            return `Execute: ${this.formConfig.name} (${this.formConfig.version})`;
        },
        errorContentPretty() {
            return JSON.stringify(this.errorContent, null, 4);
        },
        inputs() {
            return this.formConfig.inputs;
        },
        remapTitle() {
            if (this.remapAllowed === "job_produced_collection_elements") {
                return "Replace elements in collection?";
            } else {
                return "Resume dependencies from this job?";
            }
        },
        remapHelp() {
            if (this.remapAllowed === "job_produced_collection_elements") {
                return "The previous run of this tool failed. Use this option to replace the failed element(s) in the dataset collection that were produced during the previous tool run.";
            } else {
                return "The previous run of this tool failed and other tools were waiting for it to finish successfully. Use this option to resume those tools using the new output(s) of this tool run.";
            }
        },
    },
    methods: {
        emailAllowed(config, user) {
            return config.server_mail_configured && !user.isAnonymous;
        },
        reuseAllowed(user) {
            return allowCachedJobs(user.preferences);
        },
        onValidation(validationInternal) {
            this.validationInternal = validationInternal;
        },
        onChange(newData) {
            this.formData = newData;
            this.onUpdate();
        },
        onUpdate() {
            updateToolFormData(this.formConfig.id, this.currentVersion, this.history_id, this.formData).then((data) => {
                this.formConfig = data;
            });
        },
        onChangeVersion(newVersion) {
            this.requestTool(newVersion);
        },
        onUpdateFavorites(user, newFavorites) {
            user.preferences["favorites"] = newFavorites;
        },
        requestTool(newVersion) {
            this.currentVersion = newVersion || this.currentVersion;
            getToolFormData(this.id, this.currentVersion, this.job_id, this.history_id).then((data) => {
                this.formConfig = data;
                this.remapAllowed = this.job_id && data.job_remap;
                this.showLoading = false;
                this.showForm = true;
                if (newVersion) {
                    this.messageVariant = "success";
                    this.messageText = `Now you are using '${data.name}' version ${data.version}, id '${data.id}'.`;
                }
            });
        },
        onExecute(config, historyId) {
            if (this.validationInternal) {
                this.validationScrollTo = this.validationInternal.slice();
                return;
            }
            this.showExecuting = true;
            const Galaxy = getGalaxyInstance();
            const jobDef = {
                history_id: historyId,
                tool_id: this.formConfig.id,
                tool_version: this.formConfig.version,
                inputs: {
                    ...this.formData,
                },
            };
            if (this.useEmail) {
                jobDef.inputs["send_email_notification"] = true;
            }
            if (this.useJobRemapping) {
                jobDef.inputs["rerun_remap_job_id"] = this.job_id;
            }
            if (this.useCachedJobs) {
                jobDef.inputs["use_cached_job"] = true;
            }
            console.debug("toolForm::onExecute()", jobDef);
            submitJob(jobDef).then(
                (jobResponse) => {
                    if (Galaxy.currHistoryPanel) {
                        Galaxy.currHistoryPanel.refreshContents();
                    }
                    this.showForm = false;
                    if (jobResponse.produces_entry_points) {
                        this.showEntryPoints = true;
                        this.entryPoints = jobResponse.jobs;
                    }
                    const nJobs = jobResponse && jobResponse.jobs ? jobResponse.jobs.length : 0;
                    if (nJobs > 0) {
                        this.showSuccess = true;
                        this.jobDef = jobDef;
                        this.jobResponse = jobResponse;
                    } else {
                        this.showError = true;
                        this.errorTitle = "Invalid success response. No jobs found.";
                        this.errorContent = jobResponse;
                    }
                    if ([true, "true"].includes(config.enable_tool_recommendations)) {
                        this.showRecommendation = true;
                    }
                    document.querySelector(".center-panel").scrollTop = 0;
                },
                (e) => {
                    this.showExecuting = false;
                    let genericError = true;
                    const errorData = e && e.response && e.response.data && e.response.data.err_data;
                    if (errorData) {
                        const errorEntries = Object.entries(errorData);
                        if (errorEntries.length > 0) {
                            this.validationScrollTo = errorEntries[0];
                            genericError = false;
                        }
                    }
                    if (genericError) {
                        this.showError = true;
                        this.showForm = false;
                        this.errorTitle = "Job submission failed";
                        this.errorContent = this.jobDef;
                    }
                }
            );
        },
    },
};
</script>
