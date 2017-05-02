class Api::SourcesController < ApplicationController
  before_action :authenticate_user!
  before_action :find_source

  respond_to :js, only: :update

  def update
    @source.attributes = source_params
    render json: { errors: @source.errors }, status: :bad_request unless @source.save
  end

  private

  def find_source
    @source = Source.find(params.fetch(:id))
  end

  def source_params
    @_source_params ||= begin
      source_params = params.permit(:link, :name, :website,
      :brief_info, :admin_email, :admin_name, :note)
      source_params[:source_type] = SourceService.source_type(source_params[:link]) if source_params[:link]
      source_params
    end
  end
end
