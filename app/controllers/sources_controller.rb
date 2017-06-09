class SourcesController < ApplicationController
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)

  before_action :authenticate_user!, :check_permissions
  before_action :find_source, only: [:edit, :update]

  def index
    sources = Source.where(approve_state: params.fetch(:approve_state)).paginate(page: params[:page], per_page: 20)
    render cell: true, model: sources, options: { approve_state: params.fetch(:approve_state) }
  end

  def create
    source = SourceForm.new(Source.new)

    if source.validate(source_params.merge(user: current_user))
      source.save
      redirect_to sources_path(approve_state: Source.approve_state.approved)
    else
      render cell: :form, model: source
    end
  end

  def new
    source = SourceForm.new(Source.new)
    render cell: :form, model: source, options: { categories: categories }
  end

  def destroy
    Source.destroy(params[:id])
    redirect_to sources_path(approve_state: Source.approve_state.approved)
  end

  def edit
    logs = @source.source_logs.ordered
    render cell: :form, model: @source, options: { categories: categories, logs: logs }
  end

  def update
    @source.attributes = source_params
    if @source.save
      PostsFetcherJob.perform_later(@source.id)
      redirect_to sources_path(approve_state: Source.approve_state.approved)
    else
      render cell: :form, model: @source, options: { categories: categories }
    end
  end

  private

  def check_permissions
    authorize User, :admin?
  end

  def categories
    Category.all
  end

  def find_source
    @source = Source.find(params.fetch(:id))
  end

  def source_params
    @_source_params ||= begin
      source_params = params.require(:source).permit(:link, :category_id, :whitelisted, :name, :website,
      :brief_info, :admin_email, :admin_name, :note, :iframe_flag)
      source_params[:source_type] = SourceService.source_type(source_params[:link]) if source_params[:link]
      source_params[:approve_state] = Source.approve_state.approved
      source_params
    end
  end
end
