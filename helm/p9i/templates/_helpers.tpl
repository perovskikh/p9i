{{- define "p9i.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | lower -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains "." $name -}}
{{- $name | lower -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | lower -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "p9i.labels" -}}
app: {{ template "p9i.fullname" . }}
chart: {{ .Chart.Name }}
release: {{ .Release.Name }}
heritage: {{ .Release.Service }}
{{- end -}}