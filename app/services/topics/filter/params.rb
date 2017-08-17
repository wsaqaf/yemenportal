class Topics::Filter::Params
  extend ActiveModel::Naming
  extend Enumerize

  def initialize(raw_params)
    @page = raw_params[:page]
    @q = raw_params[:q]
    @set = raw_params[:set] || :highly_voted
    @time = raw_params[:time] || :daily
  end

  attr_reader :page, :q

  enumerize :set, in: [:new, :highly_voted, :most_covered], default: :highly_voted

  enumerize :time, in: [:daily, :weekly, :monthly, :all_time], default: :daily,
    predicates: true
end
