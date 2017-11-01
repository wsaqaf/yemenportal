class SourcesController < ApplicationController
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)

  before_action :authenticate_user!, :check_permissions, except: [:index]
  before_action :find_source, only: [:edit, :update, :destroy]

  def index
    sources = all_sources.by_state(params[:approve_state]).paginate(page: params[:page])
    render cell: true, model: sources, options: { current_user: current_user }
  end

  def create
    if source_form.validate(source_params.merge(user: current_user))
      source_form.save
      send_notification_email_to_admins
      redirect_to sources_path(approve_state: Source.approve_state.approved)
    else
      render cell: :form, model: source_form
    end
  end

  def new
    render cell: :form, model: source_form, options: { categories: categories }
  end

  def destroy
    @source.safe_destroy

    redirect_back(fallback_location: sources_path(approve_state: @source.approve_state),
      notice: t(".successfully_destroyed", name: @source.name))
  end

  def edit
    logs = @source.source_logs.ordered
    render cell: :form, model: @source, options: { categories: categories, logs: logs }
  end

  def update
    @source.attributes = source_params
    if @source.save
      redirect_to sources_path(approve_state: Source.approve_state.approved)
    else
      render cell: :form, model: @source, options: { categories: categories }
    end
  end

  private

  def all_sources
    policy_scope(Source).not_deleted.ordered_by_date
  end

  def check_permissions
    authorize User, :moderator?
  end

  def categories
    Category.all
  end

  def find_source
    @source = Source.not_deleted.find(params.fetch(:id))
  end

  def source_form
    @_source_form ||= SourceForm.new(Source.new)
  end

  def send_notification_email_to_admins
    SourceProposalMailer
      .notification(source: source_form.model, submitter_email: current_user.email)
      .deliver_later
  end

  def source_params
    @_source_params ||= begin
      source_params = params.require(:source).permit(:link, :category_id,
        :name, :website, :brief_info, :admin_email, :admin_name, :note, :iframe_flag,
        :logo_url)
      source_params[:source_type] = SourceService.source_type(source_params[:link]) if source_params[:link]
      source_params[:approve_state] = Source.approve_state.approved
      source_params
    end
  end
end
