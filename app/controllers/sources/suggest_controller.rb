class Sources::SuggestController < ApplicationController
  WEBSITE_REGEXP = %r((http|https){1}\:\/\/[^\/]+)
  before_action :authenticate_user!

  def create
    source = Source.new(source_params)

    if source.valid?
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
      if !source_params[:website].present? && source_params[:link]
        source_params[:website] = source_params[:link].match(WEBSITE_REGEXP).to_s
      end
      source_params
    end
  end
end