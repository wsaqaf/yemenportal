class Topics::Filter::Params
  extend ActiveModel::Naming
  extend Enumerize

  def initialize(raw_params)
    @page = raw_params[:page]
    @q = raw_params[:q]
    @set = raw_params[:set] || :most_covered
    @time = raw_params[:time] || :weekly
  end

  attr_reader :page, :q

  enumerize :set, in: [:highly_voted, :most_viewed, :most_covered], default: :most_covered

  enumerize :time, in: [:daily, :weekly, :monthly, :all_time], default: :weekly,
    predicates: true
end
