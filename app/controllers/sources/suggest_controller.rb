class Sources::SuggestController < ApplicationController
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)
  before_action :authenticate_user!

  def create
    if source_form.validate(source_params)
      source_form.save
      send_notification_email_to_admins
      set_success_notice
      redirect_to root_path
    else
      render cell: :form, model: source_form
    end
  end

  def new
    source = Source.new
    render cell: :form, model: source, options: { categories: categories }
  end

  private

  def categories
    Category.all
  end

  def source_params
    @_source_params ||= begin
      source_params = params.require(:source).permit(:link, :category_id, :name, :website,
        :brief_info, :admin_email, :admin_name, :note, :logo_url)
      source_params[:approve_state] = Source.approve_state.suggested
      source_params[:user] = current_user
      source_params
    end
  end

  def source_form
    @_source_form ||= SourceForm.new(Source.new)
  end

  def set_success_notice
    flash[:notice] = t("source.notice.success_suggest", source_name: source_form.name)
  end

  def send_notification_email_to_admins
    SourceProposalMailer
      .notification(source: source_form.model, submitter_email: current_user.email)
      .deliver_later
  end
end
