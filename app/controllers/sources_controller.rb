class SourcesController < ApplicationController
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
      render cell: "sources/form", model: source
    end
  end

  def new
    source = Source.new
    render cell: :form, model: source
  end

  def destroy
    Source.destroy(params[:id])
    redirect_to sources_path
  end

  private

  def source_params
    params.require(:source).permit(:link)
  end
end
