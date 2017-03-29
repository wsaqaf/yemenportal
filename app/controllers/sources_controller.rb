class SourcesController < ApplicationController
  before_action :find_source, only: [:edit, :update]

  def index
    sources = Source.paginate(page: params[:page], per_page: 20)
    render cell: true, model: sources
  end

  def create
    source = Source.new(source_params)

    if source.valid?
      source.save
      redirect_to sources_path
    else
      render cell: :form, model: source
    end
  end

  def new
    source = Source.new
    render cell: :form, model: source, options: { categories: categories }
  end

  def destroy
    Source.destroy(params[:id])
    redirect_to sources_path
  end

  def edit
    logs = @source.source_logs.ordered
    render cell: :form, model: @source, options: { categories: categories, logs: logs }
  end

  def update
    @source.attributes = source_params
    if @source.save
      PostsFetcherJob.perform_later(@source.id)
      redirect_to sources_path
    else
      render cell: :form, model: @source, options: { categories: categories }
    end
  end

  private

  def categories
    Category.all
  end

  def find_source
    @source = Source.find(params.fetch(:id))
  end

  def source_params
    @_source_params ||= params.require(:source).permit(:link, :category_id)
  end
end
