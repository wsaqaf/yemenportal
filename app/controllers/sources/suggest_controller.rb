class Sources::SuggestController < ApplicationController
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)
  before_action :authenticate_user!

  def create
    source = SourceForm.new(Source.new)

    if source.validate(source_params)
      source.save
      redirect_to root_path
    else
      render cell: :form, model: source
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
      :brief_info, :admin_email, :admin_name, :note)
      source_params[:approve_state] = Source.approve_state.suggested
      source_params[:user] = current_user
      source_params
    end
  end
end
